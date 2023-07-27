import { HttpClient } from '@angular/common/http';
import { Component, Input } from '@angular/core';
import { FileUploadModule } from 'primeng/fileupload';
import { API_URL } from '../env';


@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent {
  url = `${API_URL}/upload`
  
}
