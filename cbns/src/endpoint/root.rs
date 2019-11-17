use actix_web::HttpResponse;
use actix_web::Error;

pub fn root_handler() -> Result<HttpResponse, Error> {
    Ok(HttpResponse::Ok().body("<h1>404 Not Found</h1>"))
}
