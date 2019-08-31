use actix::{Recipient, Addr};

#[derive(actix::Message)]
#[rtype(usize)]
pub struct ConnectMsg {
    pub addr: Recipient<PushedMsg>,
    pub token: String
}

#[derive(actix::Message)]
pub struct DisconnectMsg {
    pub uid: usize
}

#[derive(actix::Message)]
pub struct ChannelNotificationMsg {
    pub channel: String,
    pub message: String
}

#[derive(actix::Message)]
pub struct DeviceNotificationMessage {
    pub device_token: String,
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

#[rtype(String)]
#[derive(actix::Message)]
pub struct StatusRequestMsg {

}
