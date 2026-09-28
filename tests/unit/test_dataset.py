import pandas as pd

from aethernav.datasets.io_vnbd import load_file
from aethernav.datasets.validation import split_sequences, validate_frame


def test_sample_contract(tmp_path):
    path=tmp_path/'x.csv'; pd.DataFrame({'time':[0,0.1,0.2],'lat':[13,13,13.0001],'lon':[80,80.0001,80.0001]}).to_csv(path,index=False)
    frame=load_file(path); report=validate_frame(frame)
    assert 'timestamp' in frame and report.timestamp_monotonic and report.sampling_rate_hz == 10

def test_bad_timestamp_is_reported():
    f=pd.DataFrame({'timestamp':[0,1,1], 'sequence_id':['a','a','a']}); r=validate_frame(f)
    assert r.duplicate_timestamps == 1 and not r.timestamp_monotonic

def test_sequence_split():
    f=pd.DataFrame({'timestamp':[0,1,2], 'sequence_id':['a','b','c']}); s=split_sequences(f)
    assert {item for group in s.values() for item in group} == {'a', 'b', 'c'}
