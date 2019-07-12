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

#[macro_use]
extern crate debug_rs;


use std::str::FromStr;
use std::time::Duration;

mod messages;
use messages::*;

mod notification_server;
use notification_server::*;

mod notification_session;
use notification_session::*;

#[derive(Deserialize)]
struct PostRequest {
    destination: String,
    data: String
}

fn root_handler() -> Result<HttpResponse, AWError> {
    Ok(HttpResponse::Ok().body("Hello, World!"))
}

fn socket_poll(
    req: HttpRequest,
    stream: web::Payload,
    srv: web::Data<Addr<NotificationServer>>,
) -> Result<HttpResponse, AWError> {
    ws::start(
        WSNotificationSession {
            server_address: srv.get_ref().clone(),
            uid: 0
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

fn main() -> std::io::Result<()> {
    std::env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    let system = actix::System::new("cbns");

    let server = NotificationServer::default().start();

    HttpServer::new(move || {
        App::new()
            .data(server.clone())
            .wrap(middleware::Logger::default())
            .service(web::resource("/").to(root_handler))
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
