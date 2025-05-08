from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .models import (
    Persona, Paciente, Medicamento,
    Muestra, ResultadoLaboratorio, ProcesoMedicamento
)
from .serializers import (
    PersonaSerializer, PacienteSerializer, MedicamentoSerializer,
    MuestraSerializer, ResultadoLaboratorioSerializer, ProcesoMedicamentoSerializer,
    UsuarioSerializer, RegistroPacienteSerializer
)

# -------------------------------
# ✅ Dashboards por rol
# -------------------------------


@login_required
def dashboard_paciente(request):
    try:
        persona = Persona.objects.get(usuario=request.user)
        paciente = Paciente.objects.get(persona=persona)
    except (Persona.DoesNotExist, Paciente.DoesNotExist):
        return render(request, 'core/dashboard_paciente.html', {
            'eps': '',
            'nombre': '',
            'medicamentos': [],
            'muestras': [],
            'resultados': [],
        })

    medicamentos = ProcesoMedicamento.objects.filter(paciente=paciente)
    muestras = Muestra.objects.filter(paciente=paciente)
    resultados = ResultadoLaboratorio.objects.filter(
        muestra__paciente=paciente)

    return render(request, 'core/dashboard_paciente.html', {
        'eps': paciente.eps,
        'nombre': f"{persona.nombres} {persona.apellidos}",
        'medicamentos': medicamentos,
        'muestras': muestras,
        'resultados': resultados,
    })


@login_required
def dashboard_enfermeria(request):
    # 🔹 Medicamentos para aplicar (laboratorios distintos al de pruebas clínicas)
    medicamentos = Medicamento.objects.exclude(
        laboratorio='Laboratorio Central')

    # 🔹 Muestras clínicas (laboratorio específico)
    muestras_clinicas = Medicamento.objects.filter(
        laboratorio='Laboratorio Central')

    muestras = Muestra.objects.filter(
        enfermero=request.user).order_by('-fecha_toma')
    mensaje = {}

    if request.method == 'POST':
        doc = request.POST.get('documento_paciente')
        id_med = request.POST.get('medicamento')
        obs = request.POST.get('observaciones')

        persona = Persona.objects.filter(numero_documento=doc).first()
        if not persona:
            mensaje['error'] = '❌ Paciente no encontrado.'
        else:
            paciente = Paciente.objects.filter(persona=persona).first()
            if not paciente:
                mensaje['error'] = '❌ No se encontró el paciente asociado.'
            else:
                Muestra.objects.create(
                    paciente=paciente,
                    medicamento_id=id_med,
                    enfermero=request.user,
                    observaciones=obs,
                    fecha_toma=timezone.now(),
                    enviada_laboratorio=True  # Puedes poner False si se envía luego
                )
                mensaje['exito'] = '✅ Muestra registrada correctamente.'
                muestras = Muestra.objects.filter(
                    enfermero=request.user).order_by('-fecha_toma')

    return render(request, 'core/dashboard_enfermeria.html', {
        'medicamentos': medicamentos,
        'muestras_clinicas': muestras_clinicas,
        'muestras': muestras,
        **mensaje
    })


@login_required
def dashboard_farmacia(request):
    medicamentos = Medicamento.objects.all()
    entregas = ProcesoMedicamento.objects.filter(farmacia=request.user)

    if request.method == 'POST':
        documento = request.POST['documento_paciente']
        medicamento_id = request.POST['medicamento_id']
        dosis = request.POST['dosis']
        observaciones = request.POST.get('observaciones', '')

        try:
            persona = Persona.objects.get(numero_documento=documento)
            paciente = Paciente.objects.get(persona=persona)
            medicamento = Medicamento.objects.get(id=medicamento_id)

            ProcesoMedicamento.objects.create(
                paciente=paciente,
                medicamento=medicamento,
                dosis=dosis,
                observaciones=observaciones,
                farmacia=request.user
            )
            return redirect('dashboard_farmacia')
        except Exception as e:
            print(e)

    return render(request, 'core/dashboard_farmacia.html', {
        'medicamentos': medicamentos,
        'entregas': entregas
    })


@login_required
def dashboard_laboratorio(request):
    resultados = ResultadoLaboratorio.objects.filter(laboratorio=request.user)
    muestras_disponibles = Muestra.objects.filter(
        enviada_laboratorio=True, resultadolaboratorio__isnull=True)

    if request.method == 'POST':
        muestra_id = request.POST.get('muestra_id')
        resultado = request.POST.get('resultado')

        try:
            muestra = Muestra.objects.get(id=muestra_id)
            ResultadoLaboratorio.objects.create(
                muestra=muestra,
                laboratorio=request.user,
                resultado=resultado
            )
        except Exception as e:
            print(e)

        return redirect('dashboard_laboratorio')

    return render(request, 'core/dashboard_laboratorio.html', {
        'resultados': resultados,
        'muestras_disponibles': muestras_disponibles
    })
# -------------------------------
# ✅ Login, Registro y Logout
# -------------------------------


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('redireccion_por_rol')
        else:
            return render(request, 'core/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def registro_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        rol = request.POST['rol']
        numero_documento = request.POST['numero_documento']
        eps = request.POST.get('eps', '')
        # adicionales
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        tipo_documento = request.POST.get('tipo_documento')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        sexo = request.POST.get('sexo')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')

        if User.objects.filter(username=username).exists():
            return render(request, 'core/registro.html', {'error': 'Usuario ya existe'})

        user = User.objects.create_user(username=username, password=password)
        grupo, _ = Group.objects.get_or_create(name=rol)
        user.groups.add(grupo)

        persona = Persona.objects.create(
            usuario=user,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            direccion=direccion,
            telefono=telefono
        )

        if rol == 'paciente':
            Paciente.objects.create(persona=persona, eps=eps)

        return redirect('login')
    return render(request, 'core/registro.html')

# -------------------------------
# ✅ Redirección por rol
# -------------------------------


@login_required
def redireccion_por_rol(request):
    user = request.user
    grupo = user.groups.first().name if user.groups.exists() else None
    if grupo == 'paciente':
        return redirect('dashboard_paciente')
    elif grupo == 'enfermeria':
        return redirect('dashboard_enfermeria')
    elif grupo == 'farmacia':
        return redirect('dashboard_farmacia')
    elif grupo == 'laboratorio':
        return redirect('dashboard_laboratorio')
    return redirect('login')

# -------------------------------
# 🔐 API REST para frontend o JS
# -------------------------------


class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'rol': user.groups.first().name if user.groups.exists() else 'sin_rol'
            })
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_400_BAD_REQUEST)


class RegistroPacienteAPIView(APIView):
    def post(self, request):
        serializer = RegistroPacienteSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'mensaje': 'Registro exitoso',
                'token': token.key,
                'username': user.username
            })
        return Response(serializer.errors, status=400)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


class PersonaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer
    permission_classes = [IsAuthenticated]


class PacienteListCreateAPIView(generics.ListCreateAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]


class PacienteRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]


class MedicamentoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Medicamento.objects.all()
    serializer_class = MedicamentoSerializer
    permission_classes = [IsAuthenticated]


class MuestraListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MuestraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='enfermeria').exists():
            return Muestra.objects.filter(enfermero=user)
        elif user.groups.filter(name='laboratorio').exists():
            return Muestra.objects.filter(enviada_laboratorio=True)
        return Muestra.objects.none()

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='enfermeria').exists():
            serializer.save(enfermero=self.request.user)


class ResultadoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ResultadoLaboratorioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='laboratorio').exists():
            return ResultadoLaboratorio.objects.filter(laboratorio=user)
        return ResultadoLaboratorio.objects.none()

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='laboratorio').exists():
            serializer.save(laboratorio=self.request.user)


class ProcesoMedicamentoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProcesoMedicamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='farmacia').exists():
            return ProcesoMedicamento.objects.filter(farmacia=user)
        return ProcesoMedicamento.objects.none()

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='farmacia').exists():
            serializer.save(farmacia=self.request.user)


class HistorialPacienteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.groups.filter(name='paciente').exists():
            return Response({'error': 'No autorizado'}, status=403)

        try:
            paciente = Paciente.objects.get(
                persona__numero_documento=user.username)
        except Paciente.DoesNotExist:
            return Response({'error': 'Paciente no encontrado'}, status=404)

        muestras = Muestra.objects.filter(paciente=paciente)
        resultados = ResultadoLaboratorio.objects.filter(
            muestra__paciente=paciente)
        medicamentos = ProcesoMedicamento.objects.filter(paciente=paciente)

        return Response({
            'muestras': MuestraSerializer(muestras, many=True).data,
            'resultados': ResultadoLaboratorioSerializer(resultados, many=True).data,
            'medicamentos': ProcesoMedicamentoSerializer(medicamentos, many=True).data
        })
