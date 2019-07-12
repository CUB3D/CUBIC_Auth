use actix::*;
use std::time::Duration;
use actix_web_actors::ws;
use crate::messages::{ConnectMsg, PushedMsg, DisconnectMsg};
use actix_web_actors::ws::Message;
use actix::prelude::fut;
use crate::notification_server::NotificationServer;
use crate::futures::Future;


pub struct WSNotificationSession {
    pub server_address: Addr<NotificationServer>,
    // The id of this client
    pub uid: usize
}

const DEVICE_STATUS_UPDATE_INTERVAL: Duration = Duration::from_secs(8 * 60);
//TODO: test different durations for this
// Set the delay between keep-alive pings
const DEVICE_PING_INTERVAL: Duration = Duration::from_secs(10);

impl Actor for WSNotificationSession {
    type Context = ws::WebsocketContext<Self>;

    fn started(&mut self, ctx: &mut Self::Context) {
        // Start the device notifier
        ctx.run_interval(DEVICE_STATUS_UPDATE_INTERVAL, |act, ctx | {
            ctx.text("device_update_status");
        });

        ctx.run_interval(DEVICE_PING_INTERVAL, | act, ctx | {
            debug!("Sending ping");
//            ctx.text("");
            ctx.ping("");
        });


        let addr = ctx.address();
        self.server_address
            .send(ConnectMsg {
                addr: addr.recipient(),
            }).into_actor(self)
            .then(|res, act, ctx| {
                match res {
                    Ok(uid) => act.uid = uid,
                    _ => ctx.stop(),
                }
//                match res {
//                    Ok(res) => act.id = res,
//                    _ => ctx.stop(),
//                }
                fut::ok(())
            })
            .wait(ctx);
    }

    fn stopping(&mut self, ctx: &mut Self::Context) -> Running {
        println!("Websocket DC");

        //TODO: error handling
        self.server_address.send(DisconnectMsg {
            uid: self.uid
        }).wait();//.into_actor(self).wait(ctx);

        Running::Stop
    }
}

impl Handler<PushedMsg> for WSNotificationSession {
    type Result = ();

    fn handle(&mut self, msg: PushedMsg, ctx: &mut Self::Context) {
        ctx.text(msg.message);
    }
}

impl StreamHandler<ws::Message, ws::ProtocolError> for WSNotificationSession {
    fn handle(&mut self, item: Message, ctx: &mut Self::Context) {
        println!("Got handle for stream handler")
    }
}