use actix_web::{HttpRequest, HttpResponse, web};
use crate::notification_server::NotificationServer;
use crate::notification_session::WSNotificationSession;
use actix_web_actors::ws;
use actix::Addr;
use serde::Deserialize;
use actix_web::Error;

#[derive(Deserialize)]
pub struct PollExtractor {
    token: String,
}

pub fn socket_poll(
    req: HttpRequest,
    stream: web::Payload,
    srv: web::Data<Addr<NotificationServer>>,
    path_params: web::Path<PollExtractor>
) -> Result<HttpResponse, Error> {

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
