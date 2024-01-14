import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { IFeature } from './feature';
import { Observable, catchError, throwError, BehaviorSubject } from 'rxjs';
import { API_URL } from '../env';

@Injectable({
  providedIn: 'root'
})
export class FeatureService {
  private selectedFeaturesSubject = new BehaviorSubject<IFeature[]>([]);
  selectedFeatures$ = this.selectedFeaturesSubject.asObservable();

  constructor(private http: HttpClient) { }

  getSelectedFeatures(): IFeature[] {
    return this.selectedFeaturesSubject.getValue();
  }

  setSelectedFeatures(features: IFeature[]) {
    this.selectedFeaturesSubject.next(features);
  }

  getAllFeatures(): Observable<IFeature[]> {
    return this.http.get<IFeature[]>(`${API_URL}`)
            .pipe(catchError(this.errorHandler))
  }

  executeAnnotation(features: IFeature[]) {
    return this.http.post<IFeature[]>(`${API_URL}/annotate`, { selected_features: features })
            .pipe(catchError(this.errorHandler))
  }

  getProgress(): Observable<any> {
    return this.http.get(`${API_URL}/progress`)
            .pipe(catchError(this.errorHandler));
  }

  getFeatureStatistics(): Observable<any> {
    return this.http.get(`${API_URL}/download`, { responseType: 'text' })
            .pipe(catchError(this.errorHandler));
  }

  errorHandler(error: HttpErrorResponse) {
    return throwError(() => (error.message || 'Server Error'));
  }

}
