from django.db import models

class Veiculo(models.Model):
    placa = models.CharField(max_length=10)
    modelo = models.CharField(max_length=100)
    km = models.FloatField()
    autonomia = models.FloatField()
    ultimaManutencao = models.DateField()

    def __str__(self):
        return f"self.modelo" ({self.placa})
    
class Motorista(models.Model):
    cpf = models.CharField(max_length=11, unique=True)
    nome = models.CharField(max_length=100)
    num_cnh = models.CharField(max_length=14)
    veiculoAtual = models.ForeignKey('Veiculo', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'self.nome' ({self.cpf})

class Manutencao(models.Model):
    tipoManutencao = [
    (PREVENTIVA, 'Preventiva'),
    (CORRETIVA, 'Corretiva'),
    ]

    