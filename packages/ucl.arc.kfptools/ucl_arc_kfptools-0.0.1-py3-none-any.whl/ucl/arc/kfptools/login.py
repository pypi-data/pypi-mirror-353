import os
import json
import msal

_LOCAL_KFP_CONTEXT = os.path.expanduser("~/.config/kfp/context.json")


def _load_context():
    if os.path.exists(_LOCAL_KFP_CONTEXT):
        with open(_LOCAL_KFP_CONTEXT, "r") as f:
            context = json.load(f)
        return context
    else:
        error_msg = f"context.json not found at expected path: {_LOCAL_KFP_CONTEXT}"
        raise Exception(error_msg)


def _obtain_token_from_microsoft_azure(oauth_client_id, oauth_authority):
    app = msal.PublicClientApplication(oauth_client_id, authority=oauth_authority)
    accounts = app.get_accounts()
    if accounts:
        error_msg = "did not expect multiple Microsoft Azure accounts, this is not yet implemented"
        raise Exception(error_msg)
    else:
        result = app.acquire_token_interactive(scopes=["User.Read", "email"])
    if "id_token" in result:
        return result["id_token"]
    else:
        error_msg = f"""
        failed when attempting to obtain a token from Microsoft Azure
        error: {result.get("error")}
        error_description: {result.get("error_description")}
        correlation_id: {result.get("correlation_id")}
        """
        raise Exception(error_msg)


def _write_token(id_token):
    context = _load_context()
    context["client_authentication_header_value"] = f"Bearer {id_token}"
    context["client_authentication_header_name"] = "Authorization"
    with open(_LOCAL_KFP_CONTEXT, "w") as f:
        json.dump(context, f, indent=4)


def login():
    context = _load_context()
    oauth_client_id = context.get("oauth_client_id")
    oauth_authority = context.get("oauth_authority")
    if not oauth_client_id or not oauth_authority:
        error_msg = (
            "context.json must specify both oauth_client_id and oauth_authority keys"
        )
        raise Exception(error_msg)
    id_token = _obtain_token_from_microsoft_azure(oauth_client_id, oauth_authority)
    _write_token(id_token)
