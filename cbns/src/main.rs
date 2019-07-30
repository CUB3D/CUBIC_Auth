use actix::*;

use actix_web_actors::{ws, HttpContext};
use actix_web::{HttpResponse, web, HttpRequest, HttpServer, App, Error as AWError, middleware};
use actix_web_actors::ws::Message;
use serde::Deserialize;
use futures::future::{Future, ok};
use std::net::SocketAddr;
use futures::stream::Stream;

extern crate futures;
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

#[derive(Deserialize)]
struct TokenExtractor {
    token: String
}

#[derive(Deserialize)]
struct PollExtractor {
    token: String,
}

fn root_handler() -> Result<HttpResponse, AWError> {
    Ok(HttpResponse::Ok().body("Hello, World!"))
}

fn socket_poll(
    req: HttpRequest,
    stream: web::Payload,
    srv: web::Data<Addr<NotificationServer>>,
    path_params: web::Path<PollExtractor>
) -> Result<HttpResponse, AWError> {

    let params = path_params.into_inner();

    ws::start(
        WSNotificationSession {
            server_address: srv.get_ref().clone(),
            uid: 0,
            token: params.token
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

    ok(HttpResponse::Ok().body("Ok"))
}

fn post_channel_handle(
    req: HttpRequest,
    path: web::Path<PostRequest>,
    srv: web::Data<Addr<NotificationServer>>
) -> impl Future<Item = HttpResponse, Error = AWError> {
    srv.send(NotificationMsg {
        channel: path.destination.clone(),
        message: path.data.clone()
    }).wait().unwrap();

    ok(HttpResponse::Ok().body("Ok"))
}

fn post_device_handle(
    req: HttpRequest,
    path: web::Path<PostRequest>,
    srv: web::Data<Addr<NotificationServer>>
) -> impl Future<Item = HttpResponse, Error = AWError> {
    srv.send(NotificationMsg {
        channel: path.destination.clone(),
        message: path.data.clone()
    }).wait().unwrap();

    ok(HttpResponse::Ok().body("Ok"))
}

fn message_device_status(
    srv: web::Data<Addr<NotificationServer>>,
    path: web::Path<TokenExtractor>,
) -> Result<HttpResponse, AWError> {
    let status = srv.send(DeviceStatusRequestMsg {
        token: path.token.clone()
    }).wait().unwrap();

    Ok(HttpResponse::Ok()
        .content_type("application/json; encoding=utf-8")
        .body(status))
}

fn status_handle(
    srv: web::Data<Addr<NotificationServer>>
) -> Result<HttpResponse, AWError> {
    let status = srv.send(StatusRequestMsg{}).wait().unwrap();

    Ok(HttpResponse::Ok()
        .content_type("application/json; encoding=utf-8")
        .body(status)
    )
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
            .service(web::resource("/status").route(
                web::get().to(status_handle)
            ))
            .service(web::resource("/status/{token}").route(
                web::get().to(message_device_status)
            ))
            //TODO: remove this
            .service(web::resource("/post/{destination}/{data}").route(
                web::post().to_async(message_post)
            ))
            .service(web::resource("/post/channel/{channel}").route(
                web::post().to_async(post_channel_handle)
            ))
            .service(web::resource("/post/device/{token}").route(
                web::post().to_async(post_device_handle)
            ))
    })
        .bind("0.0.0.0:8080").unwrap()
        .workers(20)
        .start();

    system.run()
}
