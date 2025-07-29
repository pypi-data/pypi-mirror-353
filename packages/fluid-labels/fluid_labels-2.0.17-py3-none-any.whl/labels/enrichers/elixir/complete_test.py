import labels.enrichers.elixir.complete
from labels.enrichers.elixir.complete import complete_package
from labels.model.package import HealthMetadata, Language, Package, PackageType
from labels.testing.mocks import Mock, mocks

MOCK_RESPONSE = {
    "meta": {
        "links": {
            "Github": "https://github.com/benoitc/hackney",
        },
        "description": "simple HTTP client",
        "licenses": [
            "Apache-2.0",
        ],
        "maintainers": [],
    },
    "name": "hackney",
    "url": "https://hex.pm/api/packages/hackney",
    "owners": [
        {
            "url": "https://hex.pm/api/users/benoitc",
            "email": "bchesneau@gmail.com",
            "username": "benoitc",
        },
    ],
    "inserted_at": "2014-08-14T21:51:54.000000Z",
    "updated_at": "2025-02-25T11:35:30.559033Z",
    "repository": "hexpm",
    "releases": [
        {
            "version": "1.23.0",
            "url": "https://hex.pm/api/packages/hackney/releases/1.23.0",
            "has_docs": True,
            "inserted_at": "2025-02-25T11:35:25.995723Z",
        },
        {
            "version": "1.22.0",
            "url": "https://hex.pm/api/packages/hackney/releases/1.22.0",
            "has_docs": True,
            "inserted_at": "2025-02-20T21:57:04.904400Z",
        },
        {
            "version": "1.21.0",
            "url": "https://hex.pm/api/packages/hackney/releases/1.21.0",
            "has_docs": False,
            "inserted_at": "2025-02-20T14:56:24.057461Z",
        },
    ],
    "downloads": {
        "all": 153680482,
        "day": 13125,
        "recent": 4630321,
        "week": 355811,
    },
    "latest_version": "1.23.0",
    "docs_html_url": "https://hexdocs.pm/hackney/",
    "retirements": {
        "1.6.4": {
            "message": None,
            "reason": "invalid",
        },
        "1.6.6": {
            "message": None,
            "reason": "invalid",
        },
    },
    "configs": {
        "erlang.mk": "dep_hackney = hex 1.23.0",
        "mix.exs": '{:hackney, "~\u003e 1.23"}',
        "rebar.config": '{hackney, "1.23.0"}',
    },
    "html_url": "https://hex.pm/packages/hackney",
    "latest_stable_version": "1.23.0",
}


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.elixir.complete,
            target="get_hex_package",
            target_type="sync",
            expected=MOCK_RESPONSE,
        ),
    ],
)
async def test_complete_package() -> None:
    package = Package(
        name="hackney",
        version="1.23.0",
        language=Language.ERLANG,
        licenses=[],
        locations=[],
        type=PackageType.HexPkg,
        p_url="pkg:hex/hackney@1.23.0",
    )

    completed_package = complete_package(package)
    assert completed_package.health_metadata
    assert completed_package.health_metadata.latest_version == "1.23.0"
    assert (
        completed_package.health_metadata.latest_version_created_at == "2025-02-25T11:35:25.995723Z"
    )
    assert completed_package.health_metadata.authors == "benoitc"
    assert completed_package.licenses == ["Apache-2.0"]


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.elixir.complete,
            target="get_hex_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_complete_package_no_response() -> None:
    package = Package(
        name="hackney",
        version="1.23.0",
        language=Language.ERLANG,
        licenses=[],
        locations=[],
        type=PackageType.HexPkg,
        p_url="pkg:hex/hackney@1.23.0",
    )

    completed_package = complete_package(package)
    assert completed_package == package


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.elixir.complete,
            target="get_hex_package",
            target_type="sync",
            expected={
                "meta": {
                    "licenses": [],
                },
                "name": "hackney",
                "url": "https://hex.pm/api/packages/hackney",
                "repository": "hexpm",
                "releases": [],
                "downloads": {},
                "latest_stable_version": "1.23.0",
                "owners": [],
            },
        ),
    ],
)
async def test_complete_package_no_optionals() -> None:
    package = Package(
        name="hackney",
        version="1.23.0",
        language=Language.ERLANG,
        licenses=[],
        locations=[],
        type=PackageType.HexPkg,
        p_url="pkg:hex/hackney@1.23.0",
    )

    completed_package = complete_package(package)
    assert completed_package.health_metadata == HealthMetadata(latest_version="1.23.0")
