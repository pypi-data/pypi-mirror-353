from __future__ import annotations

import typing as t
import uuid

from globus_cli.constants import ExplicitNullType
from globus_cli.endpointish import EntityType
from globus_cli.login_manager import LoginManager
from globus_cli.parsing import (
    ENDPOINT_PLUS_REQPATH,
    command,
    endpointish_params,
    mutex_option_group,
    one_use_option,
)
from globus_cli.termio import Field, display, print_command_hint

from ._common import validate_endpoint_create_and_update_params

COMMON_FIELDS = [Field("Message", "message"), Field("Endpoint ID", "id")]

GCP_FIELDS = [Field("Setup Key", "globus_connect_setup_key")]


@command("create", deprecated=True, hidden=True)
@endpointish_params.create(
    name="endpoint", keyword_style="string", verify_style="flag", add_legacy_params=True
)
@one_use_option(
    "--personal",
    is_flag=True,
    help=(
        "Create a Globus Connect Personal endpoint. "
        "Mutually exclusive with --server and --shared."
    ),
)
@one_use_option(
    "--server",
    is_flag=True,
    help=(
        "Create a Globus Connect Server endpoint. "
        "Mutually exclusive with --personal and --shared."
    ),
)
@one_use_option(
    "--shared",
    default=None,
    type=ENDPOINT_PLUS_REQPATH,
    help=(
        "Create a shared endpoint hosted on the given endpoint and path. "
        "Mutually exclusive with --personal and --server."
    ),
)
@mutex_option_group("--shared", "--server", "--personal")
@LoginManager.requires_login("transfer")
def endpoint_create(
    login_manager: LoginManager,
    *,
    personal: bool,
    server: bool,
    shared: tuple[uuid.UUID, str] | None,
    # endpointish setattr params
    display_name: str,
    contact_email: str | None | ExplicitNullType,
    contact_info: str | None | ExplicitNullType,
    default_directory: str | None | ExplicitNullType,
    department: str | None | ExplicitNullType,
    description: str | None | ExplicitNullType,
    disable_verify: bool | None,
    force_encryption: bool | None,
    info_link: str | None | ExplicitNullType,
    keywords: str | None,
    location: str | None,
    managed: bool | None,
    max_concurrency: int | None,
    max_parallelism: int | None,
    myproxy_dn: str | None,
    myproxy_server: str | None,
    network_use: t.Literal["normal", "minimal", "aggressive", "custom"] | None,
    oauth_server: str | None,
    organization: str | None | ExplicitNullType,
    preferred_concurrency: int | None,
    preferred_parallelism: int | None,
    public: bool,
    subscription_id: uuid.UUID | None,
    user_message: str | None | ExplicitNullType,
    user_message_link: str | None | ExplicitNullType,
) -> None:
    """
    WARNING:
    This command is deprecated. Either `globus gcp create` or the Globus Connect Server
    CLI should be used instead.

    Create a new endpoint.

    Requires a display name and exactly one of --personal, --server, or --shared to make
    a Globus Connect Personal, Globus Connect Server, or Shared endpoint respectively.

    Note that `--personal` does not perform local setup steps. When this command is run
    with the `--personal` flag, it returns a setup key which can be passed to
    Globus Connect Personal during setup.
    """
    from globus_cli.services.transfer import assemble_generic_doc

    print_command_hint(
        """\

For GCP, use one of the following replacements instead:
    globus gcp create mapped
    globus gcp create guest

For GCS, use the globus-connect-server CLI from your Endpoint."""
    )

    transfer_client = login_manager.get_transfer_client()

    endpoint_type = (
        EntityType.GCP_MAPPED
        if personal
        else EntityType.GCSV4_HOST if server else EntityType.GCSV4_SHARE
    )

    # build options into a dict for kwarg-expansion
    kwargs = ExplicitNullType.nullify_dict(
        {
            "contact_email": contact_email,
            "contact_info": contact_info,
            "default_directory": default_directory,
            "department": department,
            "description": description,
            "disable_verify": disable_verify,
            "display_name": display_name,
            "force_encryption": force_encryption,
            "info_link": info_link,
            "keywords": keywords,
            "location": location,
            "managed": managed,
            "max_concurrency": max_concurrency,
            "max_parallelism": max_parallelism,
            "myproxy_dn": myproxy_dn,
            "myproxy_server": myproxy_server,
            "network_use": network_use,
            "oauth_server": oauth_server,
            "organization": organization,
            "preferred_concurrency": preferred_concurrency,
            "preferred_parallelism": preferred_parallelism,
            "public": public,
            "subscription_id": subscription_id,
            "user_message": user_message,
            "user_message_link": user_message_link,
        }
    )
    kwargs["is_globus_connect"] = personal or None

    # validate options
    validate_endpoint_create_and_update_params(endpoint_type, False, kwargs)

    # shared endpoint creation
    if shared:
        endpoint_id, host_path = shared
        kwargs["host_endpoint"] = endpoint_id
        kwargs["host_path"] = host_path

        ep_doc = assemble_generic_doc("shared_endpoint", **kwargs)
        res = transfer_client.create_shared_endpoint(ep_doc)

    # non shared endpoint creation
    else:
        # omit `is_globus_connect` key if not GCP, otherwise include as `True`
        ep_doc = assemble_generic_doc("endpoint", **kwargs)
        res = transfer_client.create_endpoint(ep_doc)

    # output
    display(
        res,
        fields=(COMMON_FIELDS + GCP_FIELDS if personal else COMMON_FIELDS),
        text_mode=display.RECORD,
    )
