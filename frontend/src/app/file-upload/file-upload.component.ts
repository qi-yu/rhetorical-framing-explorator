import { HttpClient } from '@angular/common/http';
import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { API_URL } from '../env';
import { IFile } from './file';
import { MessageService, Message } from 'primeng/api';
import { FileService } from './file.service';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css'],
  providers: [MessageService]
})


export class FileUploadComponent implements OnInit {
  @Output() fileSelectionEvent: EventEmitter<boolean> = new EventEmitter();

  url = `${API_URL}`;
  isFileDragOver: boolean = false;
  uploadedFiles: IFile[] = [];
  filesSelectedForAnalyses: IFile[] = [];
  formData: FormData = new FormData();

  constructor(
    private http: HttpClient, 
    private messageService: MessageService, 
    private fileService: FileService) {}


  onDragEnter(event: Event) {
    event.preventDefault();
    this.isFileDragOver = true;
  }

  onDragLeave(event: Event) {
    event.preventDefault();
    this.isFileDragOver = false;
  }
  
  onUploadFiles(event: any): void {
    this.http.post<IFile>(`${this.url}/upload`, event.files).subscribe({
      next: () => {
        this.fileService.getAllFiles().subscribe((data) => {
          this.uploadedFiles = data;
          this.filesSelectedForAnalyses = data;
          this.onSelectFiles();
        });

        this.messageService.add({severity: 'success', summary: 'Success', detail: 'File(s) uploaded successfully!'});
      },

      error: () => {
        this.messageService.add({severity: 'error', summary: 'Error', detail: 'File(s) cannot be uploaded successfully!'});
      }
    });
  }

  onDeleteFiles(): void{
    for(let i = 0; i < this.filesSelectedForAnalyses.length; i++) {
      this.fileService.deleteFile(this.filesSelectedForAnalyses[i].filename).subscribe({
        next: () => {
          this.uploadedFiles = this.uploadedFiles.filter((uploadedFile) => uploadedFile.filename !== this.filesSelectedForAnalyses[i].filename);
          this.filesSelectedForAnalyses.splice(i, 1);
          this.onSelectFiles();
        },
        error: () => {
          this.messageService.add({severity: 'error', summary: 'Error', detail: 'File(s) cannot be deleted successfully!'});
        }
      })
    }
  }

  onChangeSelectionStatus(fileToChange: IFile): void {
    this.filesSelectedForAnalyses = this.filesSelectedForAnalyses.filter((file) => file.selectedForAnalyses === true);
  }

  onSelectFiles(): void {
   this.filesSelectedForAnalyses.length > 0
    ? this.fileSelectionEvent.emit(true)
    : this.fileSelectionEvent.emit(false);
  }

  ngOnInit(): void {
    this.fileService.getAllFiles()
      .subscribe((data) => {
        this.uploadedFiles = data;
        this.filesSelectedForAnalyses = data;
        this.onSelectFiles();
      })
  }
}
