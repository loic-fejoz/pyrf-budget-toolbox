from rfbudget import Amplifier, budget

def test_to_html_simplified():
    a1 = Amplifier(gain=10, iip3=20, name='A1')
    b = budget(elements=[a1])
    
    # When simplified=True (default), NF and OIP3/IIP3 should probably be hidden
    html_simple = b.to_html(options={'simplified': True})
    assert 'OutputPower' in html_simple
    assert 'OutputFrequency' not in html_simple
    assert 'Noisefigure' not in html_simple
    assert 'IIP3' not in html_simple
    assert 'OIP3' not in html_simple
    
    # When simplified=False, they should be present
    html_full = b.to_html(options={'simplified': False})
    assert 'Noisefigure' in html_full
    assert 'IIP3' in html_full
    assert 'OIP3' in html_full

if __name__ == '__main__':
    test_to_html_simplified()
