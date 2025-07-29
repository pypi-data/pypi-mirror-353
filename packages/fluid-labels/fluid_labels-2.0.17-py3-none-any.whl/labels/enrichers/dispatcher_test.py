from labels.advisories.roots import DATABASE as ROOTS_DATABASE
from labels.enrichers.dispatcher import add_package_advisories
from labels.model.file import Coordinates, DependencyType, Location
from labels.model.package import Language, Package, PackageType


async def test_get_package_advisories() -> None:
    ROOTS_DATABASE.initialize()
    package = Package(
        name="slug",
        version="0.9.0",
        locations=[
            Location(
                coordinates=Coordinates(
                    real_path="package.json",
                    line=139,
                ),
                dependency_type=DependencyType.DIRECT,
                access_path="package.json",
            ),
        ],
        language=Language.JAVASCRIPT,
        licenses=[],
        type=PackageType.NpmPkg,
        p_url="pkg:npm/slug@0.9.0",
        dependencies=None,
        found_by="javascript-parse-package-json",
    )
    result = add_package_advisories(package)
    assert result is not None
    assert len(result) > 0
    adv_cve = next((adv for adv in result if adv.id == "CVE-2017-16117"), None)
    assert adv_cve is not None
    assert adv_cve.version_constraint == ">=0 <0.9.2"
