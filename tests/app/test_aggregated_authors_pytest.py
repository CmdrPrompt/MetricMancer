import pytest
from src.kpis.model import ScanDir, File
from src.kpis.base_kpi import BaseKPI
from src.app.analyzer import AggregatedSharedOwnershipKPI

def make_file_with_authors(authors):
    kpi = AggregatedSharedOwnershipKPI('Shared Ownership', {
        'num_significant_authors': len(authors),
        'authors': authors,
        'threshold': 20.0
    })
    return File(name='dummy.py', file_path='dummy.py', kpis={'Shared Ownership': kpi})

def test_aggregated_authors_excludes_not_committed_yet():
    # Setup: two files, one with 'Not Committed Yet', one with a real author
    file1 = make_file_with_authors(['Not Committed Yet', 'Thomas Lindqvist'])
    file2 = make_file_with_authors(['Commander Prompt'])
    scan_dir = ScanDir(
        dir_name='app',
        scan_dir_path='app/',
        repo_root_path='/',
        repo_name='repo',
        files={'f1': file1, 'f2': file2}
    )

    # Aggregate authors as in analyzer.py
    authors_set = set()
    for file in scan_dir.files.values():
        if file.kpis.get('Shared Ownership') and isinstance(file.kpis['Shared Ownership'].value, dict):
            file_authors = [a for a in file.kpis['Shared Ownership'].value.get('authors', []) if a != 'Not Committed Yet']
            authors_set.update(file_authors)
    # No subdirs in this test
    aggregated_authors = list(authors_set)

    # Assert 'Not Committed Yet' is excluded
    assert 'Not Committed Yet' not in aggregated_authors
    assert 'Thomas Lindqvist' in aggregated_authors
    assert 'Commander Prompt' in aggregated_authors
    assert len(aggregated_authors) == 2
