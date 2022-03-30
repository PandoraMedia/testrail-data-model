from testrail_data_model.stats import TestRailAPIRequestStats


def test_stats_singleton_creation():
    t1 = TestRailAPIRequestStats()
    t2 = TestRailAPIRequestStats()
    assert t1 is t2


def test_stats_singleton_total():
    t1 = TestRailAPIRequestStats()
    t2 = TestRailAPIRequestStats()

    assert t2.total == t1.total
    t1.get_cases = 1000
    assert t2.total == t1.total
