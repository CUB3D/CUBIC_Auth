extern crate redis_async;

use actix::*;

use actix_web_actors::{ws, HttpContext};
use actix_web::{HttpResponse, web, HttpRequest, HttpServer, App, Error as AWError, middleware};
use actix_web_actors::ws::Message;
use serde::Deserialize;
use futures::future::{Future, ok};
use actix_redis::RedisActor;
use redis_async::client;
use std::net::SocketAddr;
use futures::stream::Stream;

extern crate futures;
extern crate tokio;
use std::str::FromStr;
use crate::redis_async::resp::FromResp;

#[derive(Deserialize)]
struct PostRequest {
    destination: String,
    data: String
}

fn socket_poll(
    req: HttpRequest,
    stream: web::Payload,
    srv: web::Data<Addr<NotificationServer>>,
) -> Result<HttpResponse, AWError> {
    ws::start(
        WSNotificationSession {
            server_address: srv.get_ref().clone()
        },
        &req,
        stream,
    )
}

fn message_post(
    req: HttpRequest,
    path: web::Path<PostRequest>,
    redis: web::Data<Addr<RedisActor>>,
    srv: web::Data<Addr<NotificationServer>>
) -> impl Future<Item = HttpResponse, Error = AWError> {

    srv.send(NotificationMsg {
        channel: path.destination.clone(),
        message: path.data.clone()
    }).wait().unwrap();

    ok(HttpResponse::InternalServerError().finish())
}

#[derive(actix::Message)]
struct ConnectMsg {
    addr: Recipient<PushedMsg>
}

#[derive(actix::Message)]
struct NotificationMsg {
    channel: String,
    message: String
}

#[derive(actix::Message)]
struct PushedMsg {
    message: String
}

struct NotificationServer {
    clients: Vec<Recipient<PushedMsg>>
}

impl Actor for NotificationServer {
    type Context = Context<Self>;
}

impl Default for NotificationServer {
    fn default() -> Self {
        NotificationServer {
            clients: Vec::new()
        }
    }
}

impl Handler<ConnectMsg> for NotificationServer {
    type Result = ();

    fn handle(&mut self, msg: ConnectMsg, _: &mut Context<Self>) -> Self::Result {
        println!("Registering new socket");

        self.clients.push(msg.addr);
    }
}

impl Handler<NotificationMsg> for NotificationServer {
    type Result = ();

    fn handle(&mut self, msg: NotificationMsg, _: &mut Context<Self>) -> Self::Result {
//        println!("Got message {} for channel {}", &msg.message, &msg.channel);

        for client in &self.clients {
            if let Err(x)  = client.do_send(PushedMsg {
                message: msg.message.clone()
            }) {
                eprintln!("Error messaging, {:?}", x)
            }
        }
    }
}

impl NotificationServer {
}


struct WSNotificationSession {
    server_address: Addr<NotificationServer>,
}

impl Actor for WSNotificationSession {
    type Context = ws::WebsocketContext<Self>;

    fn started(&mut self, ctx: &mut Self::Context) {
        println!("New websocket!");

        let addr = ctx.address();
        self.server_address
            .send(ConnectMsg {
                addr: addr.recipient(),
            }).into_actor(self)
            .then(|res, act, ctx| {
//                match res {
//                    Ok(res) => act.id = res,
//                    _ => ctx.stop(),
//                }
                fut::ok(())
            })
            .wait(ctx);
    }

    fn stopping(&mut self, _: &mut Self::Context) -> Running {
        println!("Websocket DC");
        Running::Stop
    }
}

impl Handler<PushedMsg> for WSNotificationSession {
    type Result = ();

    fn handle(&mut self, msg: PushedMsg, ctx: &mut Self::Context) {
        ctx.text(msg.message);
    }
}

impl StreamHandler<ws::Message, ws::ProtocolError> for WSNotificationSession {
    fn handle(&mut self, item: Message, ctx: &mut Self::Context) {
        println!("Got handle for stream handler")
    }
}

fn main() -> std::io::Result<()> {
//    std::env::set_var("RUST_LOG", "actix_web=info");
//    env_logger::init();

    let system = actix::System::new("cbns");

    let server = NotificationServer::default().start();

    HttpServer::new(move || {

        let redis_connection = RedisActor::start("127.0.0.1:6379");

        App::new()
            .data(server.clone())
            .data(redis_connection)
//            .wrap(middleware::Logger::default())
            .service(web::resource("/poll/{token}").to(socket_poll))
            .service(web::resource("/post/{destination}/{data}").route(
                web::post().to_async(message_post)
            ))
    })
        .bind("0.0.0.0:8080").unwrap()
        .workers(500)
        .start();


    let addr = SocketAddr::from_str("127.0.0.1:6379").unwrap();


    let msgs =
        client::pubsub_connect(&addr).and_then(move |connection| connection.subscribe("channel_device_common"));
    let the_loop = msgs.map_err(|_| ()).and_then(|msgs| {
        msgs.for_each(|message| {
            println!("{}", String::from_resp(message).unwrap());
            ok(())
        })
    });

    Arbiter::spawn(the_loop);

    system.run()
}
