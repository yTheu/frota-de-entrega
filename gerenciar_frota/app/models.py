from django.db import models

class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=100)
    km = models.PositiveIntegerField()
    autonomia = models.DecimalField(max_digits=5, decimal_places=2)
    ultimaManutencao = models.DateField()
    disponivel = models.BooleanField(default=True)
    
   
    def __str__(self):
        return f"{self.modelo} ({self.placa})"


class Motorista(models.Model):
    cpf = models.CharField(max_length=11, unique=True)
    nome = models.CharField(max_length=100)
    num_cnh = models.CharField(max_length=14)
    veiculoAtual = models.ForeignKey('Veiculo', on_delete=models.SET_NULL, null=True, blank=True)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

class Manutencao(models.Model):
    TIPO_MANUTENCAO = [
        ("PREVENTIVA", 'Preventiva'),
        ("CORRETIVA", 'Corretiva'),
    ]
    STATUS_MANUTENCAO = [
        ("PENDENTE", "Pendente"),
        ("CONCLUIDA", "Concluída"),
    ] 

    veiculo = models.ForeignKey('Veiculo', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_MANUTENCAO)
    descricao = models.TextField()
    data = models.DateField()
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="PENDENTE", choices= STATUS_MANUTENCAO)
    
   

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.veiculo.modelo} ({self.data})"

class Abastecimento(models.Model):
    litros = models.FloatField()
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    dataAbastecimento = models.DateField()
    veiculo = models.ForeignKey('Veiculo', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.veiculo} - {self.litros}L | {self.dataAbastecimento}"

class Coordenada(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"

class Entrega(models.Model):
    STATUS_ENTREGA = [
        ("PENDENTE", "Pendente"),
        ("EM_TRANSITO", "Em Trânsito"),
        ("CONCLUIDA", "Concluída"),
    ]

    origem = models.ForeignKey(Coordenada, on_delete=models.SET_NULL, null=True, related_name="origens")
    destino = models.ForeignKey(Coordenada, on_delete=models.SET_NULL, null=True, related_name="destinos")
    status = models.CharField(
        max_length=20,
        choices=STATUS_ENTREGA,
        default="PENDENTE"
    )
    veiculo = models.ForeignKey('Veiculo', on_delete=models.SET_NULL, null=True, blank=True)
   
