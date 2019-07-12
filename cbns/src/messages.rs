use actix::{Recipient, Addr};

#[derive(actix::Message)]
#[rtype(usize)]
pub struct ConnectMsg {
    pub addr: Recipient<PushedMsg>
}

#[derive(actix::Message)]
pub struct DisconnectMsg {
    pub uid: usize
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