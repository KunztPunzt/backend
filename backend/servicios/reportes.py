from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os
from typing import Dict, Any

class ServicioReportes:
    @staticmethod
    def generarReporteEstadisticas(estadisticas: Dict[str, Any], output_path: str) -> str:
        """
        Genera un reporte PDF con las estadísticas del sistema.
        
        Args:
            estadisticas: Diccionario con las estadísticas del sistema
            output_path: Ruta donde se guardará el PDF
            
        Returns:
            Ruta del archivo PDF generado
        """
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Crear documento
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20
        )
        
        # Contenido
        content = []
        
        # Título
        content.append(Paragraph("Reporte de Estadísticas del Sistema", title_style))
        content.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", subtitle_style))
        content.append(Spacer(1, 20))
        
        # Tabla de estadísticas
        data = [
            ["Métrica", "Valor"],
            ["Total de Usuarios", str(estadisticas["totalUsuarios"])],
            ["Total de Veterinarios", str(estadisticas["totalVeterinarios"])],
            ["Total de Mascotas", str(estadisticas["totalMascotas"])],
            ["Total de Citas", str(estadisticas["totalCitas"])],
            ["Citas Pendientes", str(estadisticas["citasPendientes"])],
            ["Citas Completadas", str(estadisticas["citasCompletadas"])],
            ["Citas Canceladas", str(estadisticas["citasCanceladas"])]
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(table)
        
        # Generar PDF
        doc.build(content)
        
        return output_path 