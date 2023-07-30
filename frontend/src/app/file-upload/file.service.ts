import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { IFile } from './file';
import { API_URL } from '../env';
import { Observable, catchError, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FileService {

  constructor(private http: HttpClient) { }

  getAllFiles(): Observable<IFile[]> {
    return this.http.get<IFile[]>(`${API_URL}/uploaded_files`)
            .pipe(catchError(this.errorHandler))
  }

  deleteFile(fileName: string): Observable<void> {
    const deleteUrl = `${API_URL}/delete/${fileName}`;
    return this.http.delete<void>(deleteUrl);
  }


  errorHandler(error: HttpErrorResponse) {
    return throwError(() => (error.message || 'Server Error'));
  }
}
