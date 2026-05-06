
import { registerOTel } from "@vercel/otel";

export function register() {
  registerOTel({
    serviceName: "shb_chatbot-frontend",
  });
}
