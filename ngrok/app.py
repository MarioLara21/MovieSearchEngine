import ngrok

let listener = ngrok::Session::builder()
  .authtoken_from_env()
  .connect()
  .await?
  .http_endpoint()
  .domain("my-app.ngrok.dev")
  .circuit_breaker(0.5)
  .compression()
  .deny_cidr("200.2.0.0/16")
  .oauth(OauthOptions::new("google").allow_domain("acme.com"))
  .listen()
  .await?;