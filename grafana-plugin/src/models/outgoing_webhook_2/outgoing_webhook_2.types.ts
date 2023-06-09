export interface OutgoingWebhook2 {
  authorization_header: string;
  data: string;
  forward_all: boolean;
  http_method: string;
  id: string;
  last_run: string;
  name: string;
  password: string;
  team: null;
  trigger_type: number;
  trigger_type_name: string;
  url: string;
  username: null;
  headers: string;
  trigger_template: string;
  last_response_log?: OutgoingWebhook2Response;
}

export interface OutgoingWebhook2Response {
  timestamp: string;
  url: string;
  request_trigger: string;
  request_headers: string;
  request_data: string;
  status_code: string;
  content: string;
}
