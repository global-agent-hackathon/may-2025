from fastapi import APIRouter, UploadFile, HTTPException, Query, Depends

from backend.models.requests.auth import Documents
from backend.services.files import FilesService
from fastapi.responses import FileResponse, Response
from backend.dependencies import get_files_service
from fastapi_utils.cbv import cbv
import os

files_router = APIRouter(prefix="/files", tags=["files"])


@cbv(files_router)
class FilesAPI:
    files_service: FilesService = Depends(get_files_service)

    @files_router.post("/upload/{company_name}")
    async def upload_file(self, company_name: str, file: UploadFile):
        return await self.files_service.upload_file(file, company_name)

    @files_router.get("/get-files/{company_name}", response_model=Documents)
    async def get_company_docs(self, company_name: str):
        try:
            return await self.files_service.get_company_docs(company_name)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    @files_router.get("/download")
    async def download_file(self, cloud_url: str = Query(...)):
        temp_path = await self.files_service.download_file(cloud_url)
        return FileResponse(temp_path, filename=os.path.basename(temp_path))

    @files_router.get("/iframe/{public_id}")
    async def serve_iframe(self, public_id: str):
        try:
            html_content = await self.files_service.fetch_raw_file_from_cloudinary(
                public_id
            )
            return Response(content=html_content, media_type="text/html")
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Could not fetch iframe: {e}")
