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

//TODO: make this return an object and convert that obj to json in route handler
#[rtype(String)]
#[derive(actix::Message)]
pub struct DeviceStatusRequestMsg {
    pub token: String
}