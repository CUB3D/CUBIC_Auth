use actix::*;

use actix_web_actors::{ws, HttpContext};
use actix_web::{HttpResponse, web, HttpRequest, HttpServer, App, Error as AWError, middleware};
use actix_web_actors::ws::Message;
use serde::Deserialize;
use futures::future::{Future, ok};
use std::net::SocketAddr;
use futures::stream::Stream;

extern crate futures;
extern crate tokio;
use std::str::FromStr;
use std::time::Duration;

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

const DEVICE_STATUS_UPDATE_INTERVAL: Duration = Duration::from_secs(8 * 60);

impl Actor for WSNotificationSession {
    type Context = ws::WebsocketContext<Self>;

    fn started(&mut self, ctx: &mut Self::Context) {
        println!("New websocket!");

        // Start the device notifier
        ctx.run_interval(DEVICE_STATUS_UPDATE_INTERVAL, |act, ctx | {
            ctx.text("device_update_status");
        });


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
    std::env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    let system = actix::System::new("cbns");

    let server = NotificationServer::default().start();

    HttpServer::new(move || {
        App::new()
            .data(server.clone())
            .wrap(middleware::Logger::default())
            .service(web::resource("/poll/{token}").to(socket_poll))
            .service(web::resource("/post/{destination}/{data}").route(
                web::post().to_async(message_post)
            ))
    })
        .bind("0.0.0.0:8080").unwrap()
        .workers(20)
        .start();

    system.run()
}
