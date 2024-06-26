import { HttpClient } from '@angular/common/http';
import { Component, Output, EventEmitter, OnInit, ViewChild, Input } from '@angular/core';
import { API_URL } from '../env';
import { IFile } from './file';
import { MessageService } from 'primeng/api';
import { FileService } from './file.service';
import { Table } from 'primeng/table'


@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css'],
  providers: [MessageService]
})


export class FileUploadComponent implements OnInit {
  @Output() fileSelectionEvent: EventEmitter<boolean> = new EventEmitter();
  @ViewChild('dt') dt: Table | undefined;

  url = `${API_URL}`;
  isFileDragOver: boolean = false;
  uploadedFiles: IFile[] = [];
  filesSelectedForAnalyses: IFile[] = [];
  formData: FormData = new FormData();
  clonedFiles: { [s: string]: IFile } = {};

  constructor(
    private http: HttpClient, 
    private messageService: MessageService, 
    private fileService: FileService) {}


  onDragEnter(event: Event): void {
    event.preventDefault();
    this.isFileDragOver = true;
  }

  onDragLeave(event: Event): void {
    event.preventDefault();
    this.isFileDragOver = false;
  }
  
  onUploadFiles(event: any): void {
    this.fileService.uploadFiles(event.files).subscribe({
      next: () => {
        this.fileService.getAllFiles().subscribe((data) => {
                this.uploadedFiles = data;
                this.filesSelectedForAnalyses = data;
                this.onSelectFiles();
        });
      
        this.messageService.add({severity: 'success', summary: 'Success', detail: 'File(s) uploaded successfully!'});
      },

      error: () => this.messageService.add({severity: 'error', summary: 'Error', detail: 'File(s) cannot be uploaded'}) 
    })
  }

  onDeleteFiles(): void {
    const filesToDelete = [...this.filesSelectedForAnalyses];
  
    for (const file of filesToDelete) {
      this.fileService.deleteFile(file.id).subscribe({
        next: () => {
          const indexInUploadedFiles = this.uploadedFiles.findIndex((uploadedFile) => uploadedFile.id === file.id);
          if (indexInUploadedFiles !== -1) {
            this.uploadedFiles.splice(indexInUploadedFiles, 1);
          }
  
          const indexInFilesSelectedForAnalyses = this.filesSelectedForAnalyses.indexOf(file);
          if (indexInFilesSelectedForAnalyses !== -1) {
            this.filesSelectedForAnalyses.splice(indexInFilesSelectedForAnalyses, 1);
          }
  
          this.onSelectFiles();
        },
        error: () => this.messageService.add({ severity: 'error', summary: 'Error', detail: 'File(s) cannot be deleted' })
      });
    }
  }  

  onChangeSelectionStatus(): void {
    this.filesSelectedForAnalyses = this.filesSelectedForAnalyses.filter((file) => file.selectedForAnalyses === true);
  }

  onSelectFiles(): void {
   this.filesSelectedForAnalyses.length > 0
    ? this.fileSelectionEvent.emit(true)
    : this.fileSelectionEvent.emit(false);
  }

  applyFilterGlobal($event: any, stringVal: any): void {
    if (this.dt?.rows != 0) {
      this.dt?.filterGlobal(($event.target as HTMLInputElement).value, stringVal);
    }
  }

  onRowEditInit(file: IFile): void {
    this.clonedFiles[file.id] = { ...file };
  }

  onRowEditSave(file: IFile, index: number): void {
    if (file.filename.length !== 0 && file.filename.trim() !== '') {
      this.fileService.renameFile(file.id, file.filename).subscribe({
        next: () => {
          delete this.clonedFiles[file.id];

          this.fileService.getAllFiles().subscribe((data) => {
            this.uploadedFiles = data;
            this.filesSelectedForAnalyses = data;
            this.onSelectFiles();
          })
        },
        error: () => this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to rename file' })
      })
    } else {
      this.onRowEditCancel(file, index);
      this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Invalid file name: the file name cannot be empty!' });
    }
  }

  onRowEditCancel(file: IFile, index: number): void {
    this.uploadedFiles[index] = this.clonedFiles[file.id];
    delete this.clonedFiles[file.id];
  }

  ngOnInit() {
    this.fileService.getAllFiles()
      .subscribe((data) => {
        this.uploadedFiles = data;
        this.filesSelectedForAnalyses = data;
        this.onSelectFiles();
      })
  }
}
