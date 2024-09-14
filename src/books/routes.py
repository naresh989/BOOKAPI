  
from fastapi import APIRouter,status, Depends
from fastapi.exceptions import HTTPException
from typing import Optional,List
from src.books.book_data import books
from src.books.schemas import Book,BookUpdateModel,BookCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.books.service import BookService
from src.auth.dependencies import AccessTokenBearer

book_router = APIRouter()
book_service = BookService()
access_token_bearer=AccessTokenBearer()

@book_router.get('/',response_model=list[Book])
#Depends(get_session) gets the database session for route handler
async def get_books(session:AsyncSession = Depends(get_session),user_details=Depends(access_token_bearer)):
    print(user_details)
    books =await  book_service.get_all_books(session)
    return books


@book_router.post('/' , status_code=status.HTTP_201_CREATED ,response_model=Book)
async def add_a_book(book_data : BookCreateModel , session:AsyncSession = Depends(get_session),user_details=Depends(access_token_bearer)) -> dict:
    new_book=await book_service.create_book(book_data,session)
    return new_book
    

@book_router.get('/{book_id}',response_model=Book)
async def get_book(book_id : str, session:AsyncSession = Depends(get_session),user_details=Depends(access_token_bearer))->dict:
    book = await book_service.get_book(book_id,session)
    if book:
        return book
    else:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book Not Found")

@book_router.patch('/{book_id}',response_model=Book)
async def update_book(book_id : str , updatedbook:BookUpdateModel, session:AsyncSession = Depends(get_session),user_details=Depends(access_token_bearer))->dict:
    
    updated_book = await book_service.update_book(book_id,updatedbook,session)
    if updated_book:
        return updated_book
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book Not Found")
    


@book_router.delete('/{book_id}')
async def delete_book(book_id :str, session:AsyncSession = Depends(get_session),user_details=Depends(access_token_bearer))-> str:
    book_to_delete = await book_service.delete_book(book_id,session)
    if book_to_delete:
        return None
    else:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book Not Found")


