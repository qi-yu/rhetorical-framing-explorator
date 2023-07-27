import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { IFeature } from './feature';
import { Observable, catchError, throwError } from 'rxjs';
import { API_URL } from '../env';

@Injectable({
  providedIn: 'root'
})
export class FeatureService {

  constructor(private http: HttpClient) { }

  getAllFeatures(): Observable<IFeature[]> {
    return this.http.get<IFeature[]>(`${API_URL}`)
            .pipe(catchError(this.errorHandler))
  }

  errorHandler(error: HttpErrorResponse) {
    return throwError(() => (error.message || 'Server Error'));
  }

}
