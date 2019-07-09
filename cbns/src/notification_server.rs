use actix::{Recipient, Actor, Context, Handler};
use crate::messages::{PushedMsg, ConnectMsg, NotificationMsg, DisconnectMsg};

pub struct NotificationServer {
    pub clients: Vec<Recipient<PushedMsg>>
}

impl Actor for NotificationServer {
    type Context = Context<Self>;
}

impl Default for NotificationServer {
    fn default() -> Self {
        NotificationServer {
            clients: Vec::new()
        }
    }
}

impl Handler<ConnectMsg> for NotificationServer {
    type Result = ();

    fn handle(&mut self, msg: ConnectMsg, _: &mut Context<Self>) -> Self::Result {
        println!("Registering new socket");

        self.clients.push(msg.addr);
    }
}

impl Handler<DisconnectMsg> for NotificationServer {
    type Result = ();

    fn handle(&mut self, msg: DisconnectMsg, _: &mut Context<Self>) -> Self::Result {
//        self.clients.remove()
        unimplemented!("Remove client on DC")
    }
}

impl Handler<NotificationMsg> for NotificationServer {
    type Result = ();

    fn handle(&mut self, msg: NotificationMsg, _: &mut Context<Self>) -> Self::Result {
//        println!("Got message {} for channel {}", &msg.message, &msg.channel);

        for client in &self.clients {
            if let Err(x)  = client.do_send(PushedMsg {
                message: msg.message.clone()
            }) {
                eprintln!("Error messaging, {:?}", x)
            }
        }
    }
}