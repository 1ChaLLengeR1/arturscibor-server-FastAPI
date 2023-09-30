from fastapi import APIRouter, Depends, status, Form, UploadFile
from typing import List
from fastapi.responses import JSONResponse
from JWT.authenticationRouter import check_bearer_token
from DataBase.db import SessionLocal
from DataBase.models import Projects, ImagesProjects, TechnologiesProject, FileProjects
from routers.Projects.schemas import DeleteProject, GetProjectId
import os
import random
from decouple import config
import uuid

router = APIRouter()
db = SessionLocal()


@router.get('/projects/project/get_projects')
async def get_projects():
    try:
        array_projects = []
        items_projects = db.query(Projects).all()
        for item in items_projects:
            item_object = {
                "id": item.id,
                "name_project": item.name_project,
                "short_description": item.short_description,
                "file_link": item.file_link
            }
            array_projects.append(item_object)
        return array_projects

    except(FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas pobierania projektów!"})


@router.post('/projects/project/get_project')
async def get_project(payload: GetProjectId):
    try:
        item_project_id = db.query(Projects).filter(Projects.id == payload.id)
        item_project = item_project_id.first()

        item_project_technlogies_id = db.query(TechnologiesProject).filter(
            TechnologiesProject.id_project == item_project.id)
        item_project_technology = item_project_technlogies_id.all()

        item_project_images_id = db.query(ImagesProjects).filter(ImagesProjects.id_project == item_project.id)
        item_project_images = item_project_images_id.all()
        images_frontend = []
        images_backend = []

        for image in item_project_images:
            if image.type == "Frontend":
                images_frontend.append(image)
            else:
                images_backend.append(image)

        item_project_download_file_id = db.query(FileProjects).filter(FileProjects.id_project == item_project.id)
        item_project_download_file = item_project_download_file_id.first()

        download_id = ''
        download_name = ''
        download_path = ''
        download_link = ''

        if item_project_download_file:
            download_id = item_project_download_file.id
            download_name = item_project_download_file.name
            download_path = item_project_download_file.path
            download_link = item_project_download_file.link

        return {
            "id": item_project.id,
            "name_project": item_project.name_project,
            "short_description": item_project.short_description,
            "file_image": {
                "path": item_project.file_path,
                "link": item_project.file_link
            },
            "description": item_project.description,
            "completion_data": item_project.completion_data,
            "project_number": item_project.project_number,
            "link_page": item_project.link_page,
            "level_advanced": item_project.level_advanced,
            "technologies": item_project_technology,
            "images_frontend": images_frontend,
            "images_backend": images_backend,
            "file_download": {
                "id": download_id,
                "name": download_name,
                "path": download_path,
                "link": download_link
            }
        }

    except(FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas pobierania projektu!"})


@router.put('/projects/project/update_project', dependencies=[Depends(check_bearer_token)])
async def update_project(id: str = Form(), name_project: str = Form(), short_description: str = Form(),
                         file: UploadFile = None, completion_data: str = Form(), project_number=Form(),
                         level_advanced=Form(), description: str = Form(), link_page: str = Form()):
    try:
        item_project_id = db.query(Projects).filter(Projects.id == id)
        item_project = item_project_id.first()

        if not item_project:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Brak takiego Id!"})

        item_project.name_project = name_project
        item_project.short_description = short_description
        item_project.completion_data = completion_data
        item_project.project_number = project_number
        item_project.level_advanced = level_advanced
        item_project.description = description
        item_project.link_page = link_page

        if file.size == 0 or file.filename == "brak.txt" or file is None:
            pass
        else:
            if os.path.exists(item_project.file_path):
                os.remove(item_project.file_path)

            number_random = random.random()

            file_path = f"./file/imagesproject/{number_random}-firstPhoto-{file.filename}"
            with open(file_path, "wb") as f:
                context = await file.read()
                f.write(context)

            item_project.file_path = f"./file/imagesproject/{number_random}-firstPhoto-{file.filename}"
            item_project.file_link = f"{config('SERVER')}/file/imagesproject/{number_random}-firstPhoto-{file.filename}"

        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Poprawnie z edytowano projekt!"})


    except(FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas edytowania projektu!"})


@router.post('/projects/project/add_project', dependencies=[Depends(check_bearer_token)])
async def add_project(name_project: str = Form(), short_description: str = Form(), description: str = Form(),
                      file_project_image: UploadFile = None, completion_data: str = Form(),
                      project_number: int = Form(), level_advanced: str = Form(), link_page: str = Form(),
                      technologies: List[str] = Form(),
                      images_frontend: List[UploadFile] = None, images_backend: List[UploadFile] = None,
                      file_project_download: UploadFile = None):
    try:

        path_random = random.random()
        uuid_v4 = uuid.uuid4()
        new_item = Projects(id=uuid_v4, name_project=name_project, short_description=short_description,
                            file_path=f"./file/imagesproject/{path_random}-firstPhoto-{file_project_image.filename}",
                            file_link=f"{config('SERVER')}/file/imagesproject/{path_random}-firstPhoto-{file_project_image.filename}",
                            completion_data=completion_data, project_number=project_number,
                            level_advanced=level_advanced, description=description, link_page=link_page)

        file_path_first_image = f"./file/imagesproject/{path_random}-firstPhoto-{file_project_image.filename}"
        with open(file_path_first_image, "wb") as f:
            context = await file_project_image.read()
            f.write(context)
        db.add(new_item)

        for technology in technologies:
            new_item = TechnologiesProject(id_project=uuid_v4, name=technology)
            db.add(new_item)

        for image in images_frontend:
            if image.filename == 'brak.txt' or image.size == 0 or image is None:
                pass
            else:
                new_item = ImagesProjects(id_project=uuid_v4, name=f"{image.filename}-front",
                                          path=f"./file/imagesproject/front-{uuid_v4}-{path_random}-{image.filename}",
                                          link=f"{config('SERVER')}/file/imagesproject/front-{uuid_v4}-{path_random}-{image.filename}",
                                          type="Frontend")

                file_path_image_front = f"./file/imagesproject/front-{uuid_v4}-{path_random}-{image.filename}"
                with open(file_path_image_front, "wb") as f:
                    context = await image.read()
                    f.write(context)

                db.add(new_item)

        for image in images_backend:
            if image.filename == 'brak.txt' or image.size == 0 or image is None:
                pass
            else:
                new_item = ImagesProjects(id_project=uuid_v4, name=f"{image.filename}-back",
                                          path=f"./file/imagesproject/back-{uuid_v4}-{path_random}-{image.filename}",
                                          link=f"{config('SERVER')}/file/imagesproject/back-{uuid_v4}-{path_random}-{image.filename}",
                                          type="Backend")

                file_path_image_back = f"./file/imagesproject/back-{uuid_v4}-{path_random}-{image.filename}"
                with open(file_path_image_back, "wb") as f:
                    context = await image.read()
                    f.write(context)

                db.add(new_item)

        if file_project_download.filename == 'brak.txt' or file_project_download.size == 0 or file_project_download is None:
            pass
        else:
            new_item_download = FileProjects(id_project=uuid_v4, name=file_project_download.filename,
                                             path=f"./file/downloadFilesProject/{uuid_v4}-{path_random}-{file_project_download.filename}",
                                             link=f"{config('SERVER')}/file/downloadFilesProject/{uuid_v4}-{path_random}-{file_project_download.filename}")

            file_downloadFile_path = f"./file/downloadFilesProject/{uuid_v4}-{path_random}-{file_project_download.filename}"
            with open(file_downloadFile_path, "wb") as f:
                context = await file_project_download.read()
                f.write(context)

            db.add(new_item_download)

        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Dodano poprawnie projekt!"})
    except (FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas dodawania projektu!"})


@router.delete('/projects/project/delete_project')
async def delete_project(payload: DeleteProject):
    try:

        item_id = db.query(Projects).filter(Projects.id == payload.id)
        item = item_id.first()

        if not item:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={"error": "Brak id projektu!"})

        if os.path.exists(item.file_path):
            os.remove(item.file_path)

        item_technology_id = db.query(TechnologiesProject).filter(TechnologiesProject.id_project == item.id)
        item_technology = item_technology_id.first()
        if not item_technology:
            pass
        else:
            item_technology_id.delete(synchronize_session=False)

        item_images_id = db.query(ImagesProjects).filter(ImagesProjects.id_project == item.id)
        item_image = item_images_id.first()
        if not item_image:
            pass
        else:
            item_images = item_images_id.all()
            for images in item_images:
                if os.path.exists(images.path):
                    os.remove(images.path)
            item_images_id.delete(synchronize_session=False)

        item_download_file_id = db.query(FileProjects).filter(FileProjects.id_project == item.id)
        item_download_file = item_download_file_id.first()
        if not item_download_file:
            pass
        else:
            if os.path.exists(item_download_file.path):
                os.remove(item_download_file.path)

        item_download_file_id.delete(synchronize_session=False)
        item_id.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Usunięto poprawnie projekt!"})

    except (FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas usuwania projektu!"})
