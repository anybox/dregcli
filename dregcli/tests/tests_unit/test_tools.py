import pytest

from dregcli.dregcli import Tools


@pytest.fixture()
def fixture_tags():
    return [
        'stable-1385',
        'stable-1386',
        'stable-1387',
        'stable-1388',
        'staging-1390',
        'staging-1391',
    ]


class TestTools:
    @pytest.mark.usefixtures('fixture_tags')
    def test_search(self, fixture_tags):
        # empty criteria
        res = Tools.search([], r"^stable-[0-9]{4}")
        assert res == []
        res = Tools.search([''], r"^stable-[0-9]{4}")
        assert res == []
        res = Tools.search(fixture_tags, '')
        assert res == []

        # include
        res = Tools.search(fixture_tags, r"^notin-[0-9]{4}")  # none
        assert res == []
        res = Tools.search(fixture_tags, r"^stable-[0-9]{4}")
        assert res == fixture_tags[:4]
        res = Tools.search(fixture_tags, r"^staging-[0-9]{4}")
        assert res == fixture_tags[4:]
        res = Tools.search(fixture_tags, r"^st.*-[0-9]{4}")  # all
        assert res == fixture_tags

        # exclude
        res = Tools.search(fixture_tags, r"^notin-[0-9]{4}", exclude=True)
        # by security method returns [] if no item selection
        # no implicit --all
        assert res == []

        res = Tools.search(fixture_tags, r"^stable-[0-9]{4}", exclude=True)
        assert res == fixture_tags[4:]
        res = Tools.search(fixture_tags, r"^staging-[0-9]{4}", exclude=True)
        assert res == fixture_tags[:4]

        res = Tools.search(fixture_tags, r"^st.*-[0-9]{4}", exclude=True)
        # all excluded
        assert res == []
