use actix::{Recipient, Actor, Context, Handler};
use crate::messages::{PushedMsg, ConnectMsg, NotificationMsg, DisconnectMsg};
use std::iter::Map;
use std::collections::HashMap;
use rand::Rng;

pub struct NotificationServer {
    pub clients_map: HashMap<usize, Recipient<PushedMsg>>
}

impl Actor for NotificationServer {
    type Context = Context<Self>;
}

impl Default for NotificationServer {
    fn default() -> Self {
        NotificationServer {
            clients_map: HashMap::new()
        }
    }
}

impl Handler<ConnectMsg> for NotificationServer {
    type Result = usize;

    fn handle(&mut self, msg: ConnectMsg, _: &mut Context<Self>) -> Self::Result {

        let uid = rand::thread_rng().gen();

        self.clients_map.insert(uid, msg.addr);

        println!("Registered new socket with uid '{}'", uid);

        uid
    }
}

impl Handler<DisconnectMsg> for NotificationServer {
    type Result = ();

    fn handle(&mut self, msg: DisconnectMsg, _: &mut Context<Self>) -> Self::Result {
        println!("Socket '{}' disconnected", msg.uid);

        self.clients_map.remove(&msg.uid);
    }
}

impl Handler<NotificationMsg> for NotificationServer {
    type Result = ();

    fn handle(&mut self, msg: NotificationMsg, _: &mut Context<Self>) -> Self::Result {
//        println!("Got message {} for channel {}", &msg.message, &msg.channel);

        for client in self.clients_map.values() {
            if let Err(x)  = client.do_send(PushedMsg {
                message: msg.message.clone()
            }) {
                eprintln!("Error messaging, {:?}", x)
            }
        }
    }
}