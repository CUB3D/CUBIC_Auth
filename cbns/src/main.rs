use actix::*;

use actix_web_actors::{ws, HttpContext};
use actix_web::{HttpResponse, web, HttpRequest, HttpServer, App, Error as AWError, middleware};
use actix_web_actors::ws::Message;
use serde::Deserialize;
use futures::future::{Future, ok};
use std::net::SocketAddr;
use futures::stream::Stream;
use serde_json;

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

mod notification_definition;
use notification_definition::*;

mod client_action;
use client_action::*;

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
    Ok(HttpResponse::Ok().body("Success"))
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

fn root_handle() -> Result<HttpResponse, AWError> {
    Ok(HttpResponse::Ok().body("<h1>404 Not Found</h1>"))
}

fn message_post(
    path: web::Path<PostRequest>,
    srv: web::Data<Addr<NotificationServer>>
) -> impl Future<Item = HttpResponse, Error = AWError> {

    srv.send(ChannelNotificationMsg {
        channel: path.destination.clone(),
        message: path.data.clone()
    }).wait().unwrap();

    ok(HttpResponse::Ok().body("Ok"))
}

fn post_channel_handle(
    path: web::Path<PostRequest>,
    srv: web::Data<Addr<NotificationServer>>
) -> impl Future<Item = HttpResponse, Error = AWError> {

    srv.send(ChannelNotificationMsg {
        channel: path.destination.clone(),
        message: path.data.clone()
    }).wait().unwrap();

    ok(HttpResponse::Ok().body("Ok"))
}

fn post_device_handle(
    path: web::Path<TokenExtractor>,
    notification_body: web::Json<Notification>,
    srv: web::Data<Addr<NotificationServer>>
) -> impl Future<Item = HttpResponse, Error = AWError> {

    let msg = serde_json::to_string(&notification_body.0);

    if let Ok(msg) = msg {
        srv.send(DeviceNotificationMsg {
            device_token: path.token.clone(),
            message: msg
        }).wait().unwrap();
    } else {
        println!("Unable to handle message {:?}", msg);
    }

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
        .json(status)
    )
}

fn status_handle(
    srv: web::Data<Addr<NotificationServer>>
) -> Result<HttpResponse, AWError> {
    let status = srv.send(StatusRequestMsg{}).wait().unwrap();

    Ok(HttpResponse::Ok()
        .json(status)
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
            .wrap(middleware::Compress::default())
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
            .service(web::resource("/channel/{channel}/post").route(
                web::post().to_async(post_channel_handle)
            ))
            .service(web::resource("/device/{token}/post").route(
                web::post().to_async(post_device_handle)
            ))
    })
        .bind("0.0.0.0:8080").unwrap()
        .start();

    system.run()
}
