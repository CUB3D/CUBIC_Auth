use actix::*;

use actix_web::{HttpResponse, web, HttpServer, App, Error as AWError, middleware};
use serde::Deserialize;
use futures::future::{Future, ok};

extern crate futures;
#[macro_use]
extern crate debug_rs;

mod messages;
use messages::*;

mod notification_server;
use notification_server::*;

mod notification_session;

mod notification_definition;

mod client_action;

mod endpoint;
use endpoint::socket_poll::socket_poll;
use endpoint::root::root_handler;
use endpoint::post_device::post_device_handle;
use endpoint::post_channel::post_channel_handle;

use dotenv::dotenv;

#[derive(Deserialize)]
struct PostRequest {
    destination: String,
    data: String
}

#[derive(Deserialize)]
struct TokenExtractor {
    token: String
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
    dotenv().ok();
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
