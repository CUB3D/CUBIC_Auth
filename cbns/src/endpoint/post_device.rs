use actix_web::{web, HttpResponse};
use crate::messages::DeviceNotificationMsg;
use crate::notification_definition::Notification;
use crate::notification_server::NotificationServer;
use actix::Addr;
use futures::Future;
use futures::future::ok;
use actix_web::Error;
use serde::Deserialize;

#[derive(Deserialize)]
pub struct PostDeviceExtractor {
    token: String
}

pub fn post_device_handle(
    path: web::Path<PostDeviceExtractor>,
    notification_body: web::Json<Notification>,
    srv: web::Data<Addr<NotificationServer>>
) -> impl Future<Item = HttpResponse, Error = Error> {

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
