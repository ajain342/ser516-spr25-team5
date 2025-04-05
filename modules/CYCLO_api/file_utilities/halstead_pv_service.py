import math

class HalsteadMetrics:

    @staticmethod
    def calculate(operators, operands):
        n1 = len(operators)
        n2 = len(operands)

        N1 = sum(operators.values())
        N2 = sum(operands.values())

        N = N1 + N2
        n = n1 + n2

        epsilon = 1e-10

        V = N * math.log2(n + epsilon)
        D = (n1 / 2) * (N2 / (n2 + epsilon))
        E = D * V
        
        return {
            'Difficulty': round(D, 2),
            'Effort': round(E, 2),
            'Program Length': N,
            'Program Vocabulary': n,  
            'Program Volume': round(V, 2) 
        }

    @staticmethod
    def aggregate_metrics(project_metrics):
        total_difficulty = total_effort = total_volume = 0
        total_program_length = total_vocab = 0

        for file_metrics in project_metrics.values():
            total_difficulty += file_metrics['Difficulty']
            total_effort += file_metrics['Effort']
            total_volume += file_metrics['Program Volume'] 
            total_program_length += file_metrics['Program Length']
            total_vocab += file_metrics['Program Vocabulary']  

        return {
            'Total Difficulty': round(total_difficulty, 2),
            'Total Efforts': round(total_effort, 2),
            'Total Program Volume': round(total_volume, 2),
            'Total Program Length': total_program_length,
            'Total Program Vocabulary': total_vocab
        }