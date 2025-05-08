from django.urls import path
from .views import (
    # Vistas visuales
    login_view,
    registro_view,
    redireccion_por_rol,
    dashboard_paciente,
    dashboard_enfermeria,
    dashboard_farmacia,
    dashboard_laboratorio,
    logout_view,

    # API y autenticación
    MeAPIView,
    LoginAPIView,
    RegistroPacienteAPIView,

    # API datos
    PersonaListCreateAPIView,
    PacienteListCreateAPIView,
    PacienteRetrieveUpdateAPIView,
    MedicamentoListCreateAPIView,
    MuestraListCreateAPIView,
    ResultadoListCreateAPIView,
    ProcesoMedicamentoListCreateAPIView,
    HistorialPacienteAPIView,
)

urlpatterns = [
    # 🎯 Vistas visuales
    path('', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('redirigir/', redireccion_por_rol, name='redireccion_por_rol'),

    # 🧭 Dashboards visuales por rol
    path('dashboard/paciente/', dashboard_paciente, name='dashboard_paciente'),
    path('dashboard/enfermeria/', dashboard_enfermeria,
         name='dashboard_enfermeria'),
    path('dashboard/farmacia/', dashboard_farmacia, name='dashboard_farmacia'),
    path('dashboard/laboratorio/', dashboard_laboratorio,
         name='dashboard_laboratorio'),

    # 🔐 API Token y usuario
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/me/', MeAPIView.as_view(), name='api_me'),
    path('api/registro/', RegistroPacienteAPIView.as_view(),
         name='api_registro_paciente'),

    # 👤 Persona y paciente
    path('api/personas/', PersonaListCreateAPIView.as_view(), name='api_personas'),
    path('api/pacientes/', PacienteListCreateAPIView.as_view(), name='api_pacientes'),
    path('api/pacientes/<int:pk>/',
         PacienteRetrieveUpdateAPIView.as_view(), name='api_paciente_detalle'),

    # 💊 Medicamentos
    path('api/medicamentos/', MedicamentoListCreateAPIView.as_view(),
         name='api_medicamentos'),

    # 🧪 Muestras
    path('api/muestras/', MuestraListCreateAPIView.as_view(), name='api_muestras'),

    # 🧬 Resultados de laboratorio
    path('api/resultados/', ResultadoListCreateAPIView.as_view(),
         name='api_resultados'),

    # 📦 Procesos de medicamento (entregas)
    path('api/procesos-medicamento/', ProcesoMedicamentoListCreateAPIView.as_view(),
         name='api_procesos_medicamento'),

    # 🩺 Historial del paciente
    path('api/historial/', HistorialPacienteAPIView.as_view(),
         name='api_historial_paciente'),

    path('logout/', logout_view, name='logout'),
]
