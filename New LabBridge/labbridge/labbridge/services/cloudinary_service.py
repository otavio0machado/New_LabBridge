import cloudinary
import cloudinary.uploader
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class CloudinaryService:
    def __init__(self):
        self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "")
        self.api_key = os.getenv("CLOUDINARY_API_KEY", "")
        self.api_secret = os.getenv("CLOUDINARY_API_SECRET", "")
        if self.is_configured:
            self.init_cloudinary()
        else:
            logger.warning("Cloudinary nao configurado - uploads serao desabilitados")

    @property
    def is_configured(self) -> bool:
        """Verifica se o Cloudinary está configurado"""
        return bool(self.cloud_name and self.api_key and self.api_secret)

    def init_cloudinary(self):
        """Inicializa configuração do Cloudinary usando variáveis de ambiente"""
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True
        )

    def upload_file(self, file_path: str, resource_type: str = "auto") -> Optional[str]:
        """
        Faz upload de um arquivo para o Cloudinary e retorna a URL segura.

        Args:
            file_path: Caminho do arquivo local
            resource_type: Tipo do arquivo ("auto", "image", "raw" para PDF/CSV)

        Returns:
            str: URL do arquivo no Cloudinary ou None em caso de erro
        """
        if not self.is_configured:
            logger.error("Upload falhou: Cloudinary nao configurado")
            return None
        try:
            # Upload usando upload_large para suportar arquivos > 10MB
            response = cloudinary.uploader.upload_large(
                file_path,
                resource_type=resource_type,
                folder="biodiagnostico_uploads",
                chunk_size=6000000,  # 6MB chunks
                flags="attachment:false",  # Permite visualização inline
            )
            
            url = response.get("secure_url")
            
            # Para PDFs, adicionar parâmetro fl_attachment para permitir visualização
            if url and resource_type == "raw" and file_path.endswith('.pdf'):
                # Modificar URL para forçar visualização inline
                # Adiciona fl_sanitize para melhor compatibilidade
                url = url.replace("/upload/", "/upload/fl_sanitize/")
            
            return url
            
        except Exception as e:
            logger.error(f"Erro no upload para Cloudinary: {str(e)}")
            return None
    
    def upload_pdf(self, file_path: str) -> Optional[str]:
        """
        Faz upload de um PDF de forma otimizada para visualização.
        Usa image resource_type para PDFs que permite preview.
        """
        if not self.is_configured:
            logger.error("Upload PDF falhou: Cloudinary nao configurado")
            return None
        try:
            response = cloudinary.uploader.upload_large(
                file_path,
                resource_type="image",  # image permite preview de PDFs
                folder="biodiagnostico_pdfs",
                format="pdf",
                chunk_size=6000000,
            )
            
            return response.get("secure_url")
            
        except Exception as e:
            logger.error(f"Erro no upload PDF para Cloudinary: {str(e)}")
            # Fallback para raw se image não funcionar
            return self.upload_file(file_path, resource_type="raw")
