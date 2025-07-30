from aquaview import AquaviewClient, get_datasets, get_keywords, get_sources, get_data

def test_search_basic():
    client = AquaviewClient("https://aqualink-one.vercel.app")
    result = get_datasets(client, source="IOOS", limit=1)
    assert isinstance(result, list)
    assert len(result) <= 1

def test_keywords():
    client = AquaviewClient("https://aqualink-one.vercel.app")
    result = get_keywords(client, limit=5)
    assert isinstance(result, list)

def test_sources():
    client = AquaviewClient("https://aqualink-one.vercel.app")
    result = get_sources(client)
    assert isinstance(result, list)

def test_get_data_sample():
    client = AquaviewClient("https://aqualink-one.vercel.app")
    result = get_data(client, source="IOOS", dataset_id="dfo-hal1002-20240702T1839")
    assert isinstance(result, dict) or isinstance(result, list)