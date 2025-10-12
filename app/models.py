from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilCliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_empresa = models.CharField(max_length=100, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'Perfil de Cliente para {self.user.username}'

class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=100)
    km = models.PositiveIntegerField()
    autonomia = models.DecimalField(max_digits=5, decimal_places=2)
    ultimaManutencao = models.DateField()
    status_veiculo = [
        ('DISPONIVEL', 'Disponível'),
        ('EM_ENTREGA', 'Em Entrega'),
        ('EM_MANUTENCAO', 'Em Manutenção')
    ]
    status = models.CharField(max_length=15, choices=status_veiculo, default='DISPONIVEL')
    
    def precisa_manutencao(self):
        if not self.ultimaManutencao:
            return True
        else:
            return(timezone.now().date() - self.ultimaManutencao).days - 100 #valor qlqr por enquanto

    def __str__(self):
        return f"{self.modelo} ({self.placa})"

class PerfilMotorista(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    num_cnh = models.CharField(max_length=20, unique=True)
    veiculoAtual = models.CharField(max_length=50, blank=True, null=True)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({'Disponível' if self.disponivel else 'Indisponível'})"

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
    cliente = models.ForeignKey(PerfilCliente, on_delete=models.SET_NULL, null=True, blank=True)
   
    data_inicio_prevista = models.DateTimeField()
    data_fim_prevista = models.DateTimeField()

    def restricoes(self):
        if self.veiculo and self.veiculo.status != 'DISPONIVEL':
            raise ValidationError(f'O veículo {self.veiculo.modelo} - {self.veiculo.placa} não está disponível!')