import pytest
from app.services.extractor import Extractor, ParsingException
from app.services.halstead_pv_service import HalsteadMetrics

@pytest.fixture
def sample_code():
    return """
            package com.example.graphqlserver.dto.input;

            import com.example.graphqlserver.model.Book;
            import java.util.List;

            public record AddAuthorInput(String firstName, String lastName) {
            }
            """

@pytest.fixture
def halstead_parameters(sample_code):
    ex = Extractor(sample_code)
    operators, operands = ex.get_params()
    return operators, operands

def test_calculate(halstead_parameters):
    operators, operands = halstead_parameters
    result = HalsteadMetrics.calculate(operators, operands)

    assert result['Program Length'] == 18  
    assert result['Program Vocabulary'] == 14  
    assert result['Program Volume'] == pytest.approx(68.53, rel=1e-6)  
    assert result['Difficulty'] == pytest.approx(0.0, rel=1e-6)
    assert result['Effort'] == pytest.approx(0.0, rel=1e-6)

def test_aggregate_metrics():
    project_metrics = {
        "test1.java": {'Difficulty': 2.0, 'Effort': 100, 'Program Volume': 50, 'Program Length': 15, 'Program Vocabulary': 10},
        "test2.java": {'Difficulty': 1.5, 'Effort': 60, 'Program Volume': 30, 'Program Length': 12, 'Program Vocabulary': 6}
    }
    
    aggregated_result = HalsteadMetrics.aggregate_metrics(project_metrics)
    
    assert aggregated_result['Total Difficulty'] == 3.5
    assert aggregated_result['Total Efforts'] == 160
    assert aggregated_result['Total Program Volume'] == 80  
    assert aggregated_result['Total Program Length'] == 27  
    assert aggregated_result['Total Program Vocabulary'] == 16

def test_invalid_code_handling():
    invalid_code = "public class Invalid { int x = ; }"
    
    with pytest.raises(ParsingException):
        ex = Extractor(invalid_code)
        ex.get_params()
