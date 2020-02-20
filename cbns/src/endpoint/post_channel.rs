use actix_web::{web, HttpResponse};
use crate::notification_server::NotificationServer;
use actix::Addr;
use futures::Future;
use crate::messages::ChannelNotificationMsg;
use futures::future::ok;
use serde::Deserialize;
use actix_web::Error;
use crate::notification_definition::Notification;

#[derive(Deserialize)]
pub struct PostChannelRequest {
    channel: String,
}

pub fn post_channel_handle(
    path: web::Path<PostChannelRequest>,
    notification_body: web::Json<Notification>,
    srv: web::Data<Addr<NotificationServer>>
) -> impl Future<Item = HttpResponse, Error = Error> {

    let msg = serde_json::to_string(&notification_body.0);

    if let Ok(msg) = msg {
        srv.send(ChannelNotificationMsg {
            channel: path.channel.clone(),
            message: msg,
        }).wait().unwrap();
    } else {
        println!("Unable to handle message {:?}", msg);
    }

    ok(HttpResponse::Ok().body("Ok"))
}
