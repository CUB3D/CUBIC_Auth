use actix::{Recipient, Actor, Context, Handler};
use crate::messages::{PushedMsg, ConnectMsg, NotificationMsg, DisconnectMsg, DeviceStatusRequestMsg, StatusRequestMsg};
use std::iter::Map;
use std::collections::HashMap;
use rand::Rng;

pub struct Client {
    pub identifier: String,
    pub message_recipient: Recipient<PushedMsg>,
    pub uid: usize
}

impl Client {
    pub fn new(identifier: String, message_recipient: Recipient<PushedMsg>, uid: usize) -> Client {
        Client {
            identifier,
            message_recipient,
            uid
        }
    }
}

pub struct Channel {
    pub clients: Vec<Client>
}

impl Default for Channel {
    fn default() -> Self {
        Channel {
            clients: Vec::new()
        }
    }
}

impl Channel {
    pub fn remove_by_uid(&mut self, uid: usize) {
        let index = self.clients.iter().position(| item | item.uid == uid);

        if let Some(i) = index {
            self.clients.remove(i);
        }
    }

    pub fn contains_device_by_token(&self, token: String) -> bool {
        let index = self.clients.iter().position(| item | item.identifier == token);

        return index.is_some();
    }
}

pub struct NotificationServer {
    pub channels: HashMap<String, Channel>,
}

impl Actor for NotificationServer {
    type Context = Context<Self>;
}

impl Default for NotificationServer {
    fn default() -> Self {

        let mut channels: HashMap<String, Channel> = HashMap::new();
        channels.insert("device_common".to_string(), Channel::default());

        NotificationServer {
            channels,
        }
    }
}

impl Handler<ConnectMsg> for NotificationServer {
    type Result = usize;

    fn handle(&mut self, msg: ConnectMsg, _: &mut Context<Self>) -> Self::Result {
        let uid = rand::thread_rng().gen();

        let client = Client::new(
            msg.token,
            msg.addr,
            uid
        );

        println!("Registered client '{}':{}", &client.identifier, &client.uid);

        let common_channel = self.channels.get_mut("device_common");

        if let Some(c) = common_channel {
            println!("Client '{}' registering for 'device_common'", &client.identifier);
            c.clients.push(client);
        }

        uid
    }
}

impl Handler<DisconnectMsg> for NotificationServer {
    type Result = ();

    fn handle(&mut self, msg: DisconnectMsg, _: &mut Context<Self>) -> Self::Result {
        println!("Socket '{}' disconnected", msg.uid);

        for channel in self.channels.values_mut() {
            channel.remove_by_uid(msg.uid);
        }
    }
}

impl Handler<NotificationMsg> for NotificationServer {
    type Result = ();

    fn handle(&mut self, msg: NotificationMsg, _: &mut Context<Self>) -> Self::Result {
        println!("Got message {} for channel {}", &msg.message, &msg.channel);

        let channel = self.channels.get_mut(msg.channel.as_str());

        if let Some(c) = channel {
            for client in &c.clients {
                let status = client.message_recipient.do_send(
                    PushedMsg {
                        message: msg.message.clone()
                    }
                );

                if let Err(status) = status {
                    eprintln!("Unable to send messsage to client: '{}'", client.identifier);
                }
            }
        }
    }
}

impl Handler<DeviceStatusRequestMsg> for NotificationServer {
    type Result = String;

    fn handle(&mut self, msg: DeviceStatusRequestMsg, _: &mut Context<Self>) -> Self::Result {
        for channel in self.channels.values() {
            if channel.contains_device_by_token(msg.token.clone()) {
                return "Device Connected".to_string()
            }
        }

        return "Device Not Found".to_string();
    }
}

impl Handler<StatusRequestMsg> for NotificationServer {
    type Result = String;

    fn handle(&mut self, msg: StatusRequestMsg, _: &mut Context<Self>) -> Self::Result {
//        let clients = self.token_map.keys();

        let mut s = String::new();

        for (name, channel) in &self.channels {
            s += &format!("Channel: {}", name);
            for client in &channel.clients {
                s += &format!("    Client: {}:{}", client.identifier, client.uid);
            }
        }

        s.to_string()
    }
}