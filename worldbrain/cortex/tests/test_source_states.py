import pytest

from worldbrain.cortex.models import Source, SourceStates

TEST_DOMAIN_NAME = 'test.com'


def create_source():
    source = Source(domain_name=TEST_DOMAIN_NAME)
    source.save()


def get_source():
    create_source()
    return Source.objects.get(domain_name=TEST_DOMAIN_NAME)


@pytest.mark.django_db
def test_default():
    source = get_source()
    assert source.state == SourceStates.PENDING.value


@pytest.mark.django_db
def test_ready():
    source = get_source()
    source.ready()
    assert source.state == SourceStates.READY.value


@pytest.mark.django_db
def test_crawled():
    source = get_source()
    source.ready()
    source.crawl()
    assert source.state == SourceStates.CRAWLED.value


@pytest.mark.django_db
def test_complete():
    source = get_source()
    source.ready()
    source.crawl()
    source.complete()
    assert source.state == SourceStates.CONTENT_COMPLETE.value


@pytest.mark.django_db
def test_index():
    source = get_source()
    source.ready()
    source.crawl()
    source.complete()
    source.index()
    assert source.state == SourceStates.INDEXED.value


@pytest.mark.django_db
def test_pending_reject():
    source = get_source()
    source.reject()
    assert source.state == SourceStates.REJECTED.value


@pytest.mark.django_db
def test_ready_reject():
    source = get_source()
    source.ready()
    source.reject()
    assert source.state == SourceStates.REJECTED.value


@pytest.mark.django_db
def test_crawled_reject():
    source = get_source()
    source.ready()
    source.crawl()
    source.reject()
    assert source.state == SourceStates.REJECTED.value


@pytest.mark.django_db
def test_complete_reject():
    source = get_source()
    source.ready()
    source.crawl()
    source.complete()
    source.reject()
    assert source.state == SourceStates.REJECTED.value


@pytest.mark.django_db
def test_indexed_reject():
    source = get_source()
    source.ready()
    source.crawl()
    source.complete()
    source.index()
    source.reject()
    assert source.state == SourceStates.REJECTED.value


@pytest.mark.django_db
def test_pending_fail():
    source = get_source()
    source.fail()
    assert source.state == SourceStates.FAILED.value


@pytest.mark.django_db
def test_ready_fail():
    source = get_source()
    source.ready()
    source.fail()
    assert source.state == SourceStates.FAILED.value


@pytest.mark.django_db
def test_crawled_fail():
    source = get_source()
    source.ready()
    source.crawl()
    source.fail()
    assert source.state == SourceStates.FAILED.value


@pytest.mark.django_db
def test_complete_fail():
    source = get_source()
    source.ready()
    source.crawl()
    source.complete()
    source.fail()
    assert source.state == SourceStates.FAILED.value


@pytest.mark.django_db
def test_indexed_fail():
    source = get_source()
    source.ready()
    source.crawl()
    source.complete()
    source.index()
    source.fail()
    assert source.state == SourceStates.FAILED.value
