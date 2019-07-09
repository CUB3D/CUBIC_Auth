use actix::{Recipient, Addr};

#[derive(actix::Message)]
pub struct ConnectMsg {
    pub addr: Recipient<PushedMsg>
}

#[derive(actix::Message)]
pub struct DisconnectMsg {
    pub addr: Recipient<PushedMsg>
}

#[derive(actix::Message)]
pub struct NotificationMsg {
    pub channel: String,
    pub message: String
}

#[derive(actix::Message)]
pub struct PushedMsg {
    pub message: String
}