from unittest.mock import patch

from labels.enrichers.python import complete
from labels.enrichers.python.complete import complete_package
from labels.model.package import Artifact, Digest, HealthMetadata, Language, Package, PackageType
from labels.testing.mocks import Mock, mocks

MOCK_RESPONSE_ALL = {
    "info": {
        "author": "Development",
        "author_email": "development@fluidattacks.com",
        "bugtrack_url": None,
        "classifiers": [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
        ],
        "description": "",
        "description_content_type": None,
        "docs_url": None,
        "download_url": None,
        "downloads": {
            "last_day": -1,
            "last_month": -1,
            "last_week": -1,
        },
        "dynamic": None,
        "home_page": None,
        "keywords": None,
        "license": "MPL-2.0",
        "license_expression": None,
        "license_files": None,
        "maintainer": None,
        "maintainer_email": None,
        "name": "fluid-labels",
        "package_url": "https://pypi.org/project/fluid-labels/",
        "platform": None,
        "project_url": "https://pypi.org/project/fluid-labels/",
        "project_urls": None,
        "provides_extra": None,
        "release_url": "https://pypi.org/project/fluid-labels/2.0.11/",
        "requires_dist": [
            "aioboto3==14.1.0",
            "beautifulsoup4==4.13.4",
            "boto3==1.37.0",
        ],
        "requires_python": "\u003c4.0,\u003e=3.11",
        "summary": "Fluid Attacks SBOM Library",
        "version": "2.0.11",
        "yanked": False,
        "yanked_reason": None,
    },
    "last_serial": 29160427,
    "releases": {
        "2.0.9": [
            {
                "comment_text": "",
                "digests": {
                    "blake2b_256": "0337047eede6e920bbc716580e5a3e7f1f4a8632c2cae56b2bc1cf4e5acd"
                    "386b",
                    "md5": "7943bc963cbbef6dbf24dc4c26f94c03",
                    "sha256": "a6f3bee589edd30203b148b930fee03803e8a5c1c3e1d06643a8f05180f684b4",
                },
                "downloads": -1,
                "filename": "fluid_labels-2.0.9-py3-none-any.whl",
                "has_sig": False,
                "md5_digest": "7943bc963cbbef6dbf24dc4c26f94c03",
                "packagetype": "bdist_wheel",
                "python_version": "py3",
                "requires_python": "\u003c4.0,\u003e=3.11",
                "size": 235501,
                "upload_time": "2025-05-14T18:43:30",
                "upload_time_iso_8601": "2025-05-14T18:43:30.467122Z",
                "url": "https://files.pythonhosted.org/packages/03/37/047eede6e920bbc716580e5a3e7"
                "f1f4a8632c2cae56b2bc1cf4e5acd386b/fluid_labels-2.0.9-py3-none-any.whl",
                "yanked": False,
                "yanked_reason": None,
            },
            {
                "comment_text": "",
                "digests": {
                    "blake2b_256": "9d46164d41496dbdd1a715ab0b16746c02ae6928cc0cd411fc823cd2f71"
                    "d1f1b",
                    "md5": "00d6b9e9b15f035fa7e1f81ff6152d76",
                    "sha256": "8fc60e9efe69cf1aca629e9d458e1c55d71a3f77b8d8474f73fdc75856bf98b9",
                },
                "downloads": -1,
                "filename": "fluid_labels-2.0.9.tar.gz",
                "has_sig": False,
                "md5_digest": "00d6b9e9b15f035fa7e1f81ff6152d76",
                "packagetype": "sdist",
                "python_version": "source",
                "requires_python": "\u003c4.0,\u003e=3.11",
                "size": 140818,
                "upload_time": "2025-05-14T18:43:31",
                "upload_time_iso_8601": "2025-05-14T18:43:31.998717Z",
                "url": "https://files.pythonhosted.org/packages/9d/46/164d41496dbdd1a715ab0b167"
                "46c02ae6928cc0cd411fc823cd2f71d1f1b/fluid_labels-2.0.9.tar.gz",
                "yanked": False,
                "yanked_reason": None,
            },
        ],
        "2.0.11": [
            {
                "comment_text": "",
                "digests": {
                    "blake2b_256": "73674b43b7e1fac3baee6a8c7b8e6b3b81cedae9e9e78f0b32c60f170b0"
                    "625b1",
                    "md5": "1aed40cc1d62e7260f39a88df53f49a6",
                    "sha256": "bd4f363c9db83e65a8060b5f5955222a7010029e84a4b8451eb8d45244188b9e",
                },
                "downloads": -1,
                "filename": "fluid_labels-2.0.11-py3-none-any.whl",
                "has_sig": False,
                "md5_digest": "1aed40cc1d62e7260f39a88df53f49a6",
                "packagetype": "bdist_wheel",
                "python_version": "py3",
                "requires_python": "\u003c4.0,\u003e=3.11",
                "size": 236397,
                "upload_time": "2025-05-20T15:16:38",
                "upload_time_iso_8601": "2025-05-20T15:16:38.256532Z",
                "url": "https://files.pythonhosted.org/packages/73/67/4b43b7e1fac3baee6a8c7b8e6b3b81"
                "cedae9e9e78f0b32c60f170b0625b1/fluid_labels-2.0.11-py3-none-any.whl",
                "yanked": False,
                "yanked_reason": None,
            },
            {
                "comment_text": "",
                "digests": {
                    "blake2b_256": "b0cbc2a7a7685253d9e0ccbc6a81e41bc216ce5a48f1043a5fb9c583007"
                    "59387",
                    "md5": "5bad93b32e18b1dc1dc3d4edaceebedb",
                    "sha256": "9ba76ca61a0fea6e0190d305ef30df465081494ff5761ee7ececb8acfeac5d13",
                },
                "downloads": -1,
                "filename": "fluid_labels-2.0.11.tar.gz",
                "has_sig": False,
                "md5_digest": "5bad93b32e18b1dc1dc3d4edaceebedb",
                "packagetype": "sdist",
                "python_version": "source",
                "requires_python": "\u003c4.0,\u003e=3.11",
                "size": 141942,
                "upload_time": "2025-05-20T15:16:39",
                "upload_time_iso_8601": "2025-05-20T15:16:39.746295Z",
                "url": "https://files.pythonhosted.org/packages/b0/cb/c2a7a7685253d9e0ccbc6a81e41"
                "bc216ce5a48f1043a5fb9c58300759387/fluid_labels-2.0.11.tar.gz",
                "yanked": False,
                "yanked_reason": None,
            },
        ],
    },
    "urls": [
        {
            "comment_text": "",
            "digests": {
                "blake2b_256": "73674b43b7e1fac3baee6a8c7b8e6b3b81cedae9e9e78f0b32c60f170b0625b1",
                "md5": "1aed40cc1d62e7260f39a88df53f49a6",
                "sha256": "bd4f363c9db83e65a8060b5f5955222a7010029e84a4b8451eb8d45244188b9e",
            },
            "downloads": -1,
            "filename": "fluid_labels-2.0.11-py3-none-any.whl",
            "has_sig": False,
            "md5_digest": "1aed40cc1d62e7260f39a88df53f49a6",
            "packagetype": "bdist_wheel",
            "python_version": "py3",
            "requires_python": "\u003c4.0,\u003e=3.11",
            "size": 236397,
            "upload_time": "2025-05-20T15:16:38",
            "upload_time_iso_8601": "2025-05-20T15:16:38.256532Z",
            "url": "https://files.pythonhosted.org/packages/73/67/4b43b7e1fac3baee6a8c7b8e6b3b81c"
            "edae9e9e78f0b32c60f170b0625b1/fluid_labels-2.0.11-py3-none-any.whl",
            "yanked": False,
            "yanked_reason": None,
        },
        {
            "comment_text": "",
            "digests": {
                "blake2b_256": "b0cbc2a7a7685253d9e0ccbc6a81e41bc216ce5a48f1043a5fb9c58300759387",
                "md5": "5bad93b32e18b1dc1dc3d4edaceebedb",
                "sha256": "9ba76ca61a0fea6e0190d305ef30df465081494ff5761ee7ececb8acfeac5d13",
            },
            "downloads": -1,
            "filename": "fluid_labels-2.0.11.tar.gz",
            "has_sig": False,
            "md5_digest": "5bad93b32e18b1dc1dc3d4edaceebedb",
            "packagetype": "sdist",
            "python_version": "source",
            "requires_python": "\u003c4.0,\u003e=3.11",
            "size": 141942,
            "upload_time": "2025-05-20T15:16:39",
            "upload_time_iso_8601": "2025-05-20T15:16:39.746295Z",
            "url": "https://files.pythonhosted.org/packages/b0/cb/c2a7a7685253d9e0ccbc6a81e41bc216"
            "ce5a48f1043a5fb9c58300759387/fluid_labels-2.0.11.tar.gz",
            "yanked": False,
            "yanked_reason": None,
        },
    ],
    "vulnerabilities": [],
}


MOCK_RESPONSE_CURRENT = {
    "info": {
        "author": "Development",
        "author_email": "development@fluidattacks.com",
        "bugtrack_url": None,
        "classifiers": [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
        ],
        "description": "",
        "description_content_type": None,
        "docs_url": None,
        "download_url": None,
        "downloads": {
            "last_day": -1,
            "last_month": -1,
            "last_week": -1,
        },
        "dynamic": None,
        "home_page": None,
        "keywords": None,
        "license": "MPL-2.0",
        "license_expression": None,
        "license_files": None,
        "maintainer": None,
        "maintainer_email": None,
        "name": "fluid-labels",
        "package_url": "https://pypi.org/project/fluid-labels/",
        "platform": None,
        "project_url": "https://pypi.org/project/fluid-labels/",
        "project_urls": None,
        "provides_extra": None,
        "release_url": "https://pypi.org/project/fluid-labels/2.0.9/",
        "requires_dist": [
            "aioboto3==14.1.0",
            "beautifulsoup4==4.13.4",
            "boto3==1.37.0",
            "bugsnag==4.7.1",
        ],
        "requires_python": "\u003c4.0,\u003e=3.11",
        "summary": "Fluid Attacks SBOM Library",
        "version": "2.0.9",
        "yanked": False,
        "yanked_reason": None,
    },
    "last_serial": 29160427,
    "urls": [
        {
            "comment_text": "",
            "digests": {
                "blake2b_256": "0337047eede6e920bbc716580e5a3e7f1f4a8632c2cae56b2bc1cf4e5acd386b",
                "md5": "7943bc963cbbef6dbf24dc4c26f94c03",
                "sha256": "a6f3bee589edd30203b148b930fee03803e8a5c1c3e1d06643a8f05180f684b4",
            },
            "downloads": -1,
            "filename": "fluid_labels-2.0.9-py3-none-any.whl",
            "has_sig": False,
            "md5_digest": "7943bc963cbbef6dbf24dc4c26f94c03",
            "packagetype": "bdist_wheel",
            "python_version": "py3",
            "requires_python": "\u003c4.0,\u003e=3.11",
            "size": 235501,
            "upload_time": "2025-05-14T18:43:30",
            "upload_time_iso_8601": "2025-05-14T18:43:30.467122Z",
            "url": "https://files.pythonhosted.org/packages/03/37/047eede6e920bbc716580e5a3e7f1f4"
            "a8632c2cae56b2bc1cf4e5acd386b/fluid_labels-2.0.9-py3-none-any.whl",
            "yanked": False,
            "yanked_reason": None,
        },
        {
            "comment_text": "",
            "digests": {
                "blake2b_256": "9d46164d41496dbdd1a715ab0b16746c02ae6928cc0cd411fc823cd2f71d1f1b",
                "md5": "00d6b9e9b15f035fa7e1f81ff6152d76",
                "sha256": "8fc60e9efe69cf1aca629e9d458e1c55d71a3f77b8d8474f73fdc75856bf98b9",
            },
            "downloads": -1,
            "filename": "fluid_labels-2.0.9.tar.gz",
            "has_sig": False,
            "md5_digest": "00d6b9e9b15f035fa7e1f81ff6152d76",
            "packagetype": "sdist",
            "python_version": "source",
            "requires_python": "\u003c4.0,\u003e=3.11",
            "size": 140818,
            "upload_time": "2025-05-14T18:43:31",
            "upload_time_iso_8601": "2025-05-14T18:43:31.998717Z",
            "url": "https://files.pythonhosted.org/packages/9d/46/164d41496dbdd1a715ab0b16746c02ae"
            "6928cc0cd411fc823cd2f71d1f1b/fluid_labels-2.0.9.tar.gz",
            "yanked": False,
            "yanked_reason": None,
        },
    ],
    "vulnerabilities": [],
}


def test_complete_package() -> None:
    package = Package(
        name="fluid-labels",
        version="2.0.8",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/fluid-labels@2.0.8",
    )

    expected_health_metadata = HealthMetadata(
        latest_version="2.0.11",
        latest_version_created_at="2025-05-20T15:16:38.256532Z",
        authors="Development <development@fluidattacks.com>",
        artifact=Artifact(
            url="https://files.pythonhosted.org/packages/9d/46/164d41496dbdd1a715ab0b16746c02ae6928"
            "cc0cd411fc823cd2f71d1f1b/fluid_labels-2.0.9.tar.gz",
            integrity=Digest(
                algorithm="sha256",
                value="8fc60e9efe69cf1aca629e9d458e1c55d71a3f77b8d8474f73fdc75856bf98b9",
            ),
        ),
    )

    with patch("labels.enrichers.python.complete.get_pypi_package") as mock_get_pypi:
        mock_get_pypi.side_effect = [MOCK_RESPONSE_ALL, MOCK_RESPONSE_CURRENT]

        completed_package = complete_package(package)
        assert completed_package.health_metadata == expected_health_metadata
        assert completed_package.licenses == ["MPL-2.0"]


def test_complete_package_no_author() -> None:
    package = Package(
        name="fluid-labels",
        version="2.0.8",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/fluid-labels@2.0.8",
    )

    mock_response_all_no_author = {
        "info": {
            "author": None,
            "author_email": "development@fluidattacks.com",
            "version": "2.0.11",
            "license": "MPL-2.0",
        },
        "releases": {
            "2.0.11": [
                {
                    "upload_time_iso_8601": "2025-05-20T15:16:38.256532Z",
                },
            ],
        },
        "urls": [],
    }

    expected_health_metadata = HealthMetadata(
        latest_version="2.0.11",
        latest_version_created_at="2025-05-20T15:16:38.256532Z",
        authors="development@fluidattacks.com",
        artifact=Artifact(
            url="https://files.pythonhosted.org/packages/9d/46/164d41496dbdd1a715ab0b16746c02ae692"
            "8cc0cd411fc823cd2f71d1f1b/fluid_labels-2.0.9.tar.gz",
            integrity=Digest(
                algorithm="sha256",
                value="8fc60e9efe69cf1aca629e9d458e1c55d71a3f77b8d8474f73fdc75856bf98b9",
            ),
        ),
    )

    with patch("labels.enrichers.python.complete.get_pypi_package") as mock_get_pypi:
        mock_get_pypi.side_effect = [mock_response_all_no_author, MOCK_RESPONSE_CURRENT]

        completed_package = complete_package(package)
        assert completed_package.health_metadata == expected_health_metadata
        assert completed_package.licenses == ["MPL-2.0"]


def test_complete_package_invalid_info() -> None:
    package = Package(
        name="fluid-labels",
        version="2.0.8",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/fluid-labels@2.0.8",
    )

    mock_response_all_invalid: dict = {
        "info": None,
        "releases": {},
        "urls": [],
    }

    with patch("labels.enrichers.python.complete.get_pypi_package") as mock_get_pypi:
        mock_get_pypi.side_effect = [mock_response_all_invalid, MOCK_RESPONSE_CURRENT]

        completed_package = complete_package(package)
        assert completed_package.health_metadata is None
        assert completed_package.licenses == []


def test_complete_package_invalid_releases() -> None:
    package = Package(
        name="fluid-labels",
        version="2.0.8",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/fluid-labels@2.0.8",
    )

    mock_response_all_invalid: dict = {
        "info": {
            "version": "2.0.11",
            "author": "Development",
            "author_email": "development@fluidattacks.com",
            "license": "MPL-2.0",
        },
        "releases": None,
        "urls": [],
    }

    expected_health_metadata = HealthMetadata(
        latest_version="2.0.11",
        latest_version_created_at=None,
        authors="Development <development@fluidattacks.com>",
        artifact=Artifact(
            url="https://files.pythonhosted.org/packages/9d/46/164d41496dbdd1a715ab0b16746c02ae69"
            "28cc0cd411fc823cd2f71d1f1b/fluid_labels-2.0.9.tar.gz",
            integrity=Digest(
                algorithm="sha256",
                value="8fc60e9efe69cf1aca629e9d458e1c55d71a3f77b8d8474f73fdc75856bf98b9",
            ),
        ),
    )

    with patch("labels.enrichers.python.complete.get_pypi_package") as mock_get_pypi:
        mock_get_pypi.side_effect = [mock_response_all_invalid, MOCK_RESPONSE_CURRENT]

        completed_package = complete_package(package)
        assert completed_package.health_metadata == expected_health_metadata
        assert completed_package.licenses == ["MPL-2.0"]


def test_complete_package_invalid_time_value() -> None:
    package = Package(
        name="fluid-labels",
        version="2.0.8",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/fluid-labels@2.0.8",
    )

    mock_response_all_invalid: dict = {
        "info": {
            "version": "2.0.11",
            "author": "Development",
            "author_email": "development@fluidattacks.com",
            "license": "MPL-2.0",
        },
        "releases": {
            "2.0.11": [
                {
                    "upload_time_iso_8601": 123,
                },
            ],
        },
        "urls": [],
    }

    expected_health_metadata = HealthMetadata(
        latest_version="2.0.11",
        latest_version_created_at=None,
        authors="Development <development@fluidattacks.com>",
        artifact=Artifact(
            url="https://files.pythonhosted.org/packages/9d/46/164d41496dbdd1a715ab0b16746c02ae69"
            "28cc0cd411fc823cd2f71d1f1b/fluid_labels-2.0.9.tar.gz",
            integrity=Digest(
                algorithm="sha256",
                value="8fc60e9efe69cf1aca629e9d458e1c55d71a3f77b8d8474f73fdc75856bf98b9",
            ),
        ),
    )

    with patch("labels.enrichers.python.complete.get_pypi_package") as mock_get_pypi:
        mock_get_pypi.side_effect = [mock_response_all_invalid, MOCK_RESPONSE_CURRENT]

        completed_package = complete_package(package)
        assert completed_package.health_metadata == expected_health_metadata
        assert completed_package.licenses == ["MPL-2.0"]


def test_complete_package_no_licenses() -> None:
    package = Package(
        name="fluid-labels",
        version="2.0.8",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/fluid-labels@2.0.8",
    )

    mock_response_all_no_license: dict = {
        "info": {
            "version": "2.0.11",
            "author": "Development",
            "author_email": "development@fluidattacks.com",
            "license": None,
        },
        "releases": {
            "2.0.11": [
                {
                    "upload_time_iso_8601": "2025-05-20T15:16:38.256532Z",
                },
            ],
        },
        "urls": [],
    }

    expected_health_metadata = HealthMetadata(
        latest_version="2.0.11",
        latest_version_created_at="2025-05-20T15:16:38.256532Z",
        authors="Development <development@fluidattacks.com>",
        artifact=Artifact(
            url="https://files.pythonhosted.org/packages/9d/46/164d41496dbdd1a715ab0b16746c02ae6928"
            "cc0cd411fc823cd2f71d1f1b/fluid_labels-2.0.9.tar.gz",
            integrity=Digest(
                algorithm="sha256",
                value="8fc60e9efe69cf1aca629e9d458e1c55d71a3f77b8d8474f73fdc75856bf98b9",
            ),
        ),
    )

    with patch("labels.enrichers.python.complete.get_pypi_package") as mock_get_pypi:
        mock_get_pypi.side_effect = [mock_response_all_no_license, MOCK_RESPONSE_CURRENT]

        completed_package = complete_package(package)
        assert completed_package.health_metadata == expected_health_metadata
        assert completed_package.licenses == []


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_pypi_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_complete_package_no_pypi_response() -> None:
    package = Package(
        name="fluid-labels",
        version="2.0.8",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/fluid-labels@2.0.8",
    )

    completed_package = complete_package(package)
    assert completed_package == package
    assert completed_package.health_metadata is None
    assert completed_package.licenses == []
