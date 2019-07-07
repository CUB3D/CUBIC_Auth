use std::thread::sleep;
use std::time::Duration;
use redis::{Commands, Client, Connection, RedisError};

fn get_redis_client() -> Client {
    let mut client = redis::Client::open("redis://redis:6379/");

    while client.is_err() {
        println!("Waiting 5s for client");
        sleep(Duration::from_secs(5));
        client = redis::Client::open("redis://redis:6379/");
    }

    return client.unwrap();
}

fn get_redis_connection() -> Connection {
    let client = get_redis_client();

    let mut conn = client.get_connection();

    while conn.is_err() {
        println!("Waiting 5s for connection");
        sleep(Duration::from_secs(5));
        conn = client.get_connection();
    }

    return conn.unwrap();
}

fn main() {
    let con = get_redis_connection();

    loop {
        let pub_result: Result<(), RedisError> = con.publish("channel_device_common", "device_update_status");

        if let Err(x) = pub_result {
            println!("Failed to send update: {:?}", x)
        }

        sleep(Duration::from_secs(10))
    }
}
