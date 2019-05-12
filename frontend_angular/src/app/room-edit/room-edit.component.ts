import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, ParamMap, Router} from '@angular/router';

import 'rxjs/add/operator/takeWhile';
import 'rxjs/add/operator/switchMap';

import {RoomService} from '../api/api/room.service';
import {Room} from '../api/model/room';
import {NotificationsService} from 'angular2-notifications';

@Component({
  selector: 'app-room-edit',
  templateUrl: './room-edit.component.html',
  styleUrls: ['./room-edit.component.css']
})

export class RoomEditComponent implements OnInit, OnDestroy {

  disabled = false;
  roomNumber: number;
  roomEdit: FormGroup;
  private alive = true;
  private room: Room;

  constructor(
    public roomService: RoomService,
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private notif: NotificationsService,
  ) {
    this.createForm();
  }

  createForm() {
    this.disabled = false;
    this.roomEdit = this.fb.group({
      roomNumber: ['', [Validators.min(1000), Validators.max(9999), Validators.required]],
      vlan: ['', [Validators.min(0), Validators.max(100), Validators.required]],
      description: ['', Validators.required],
    });
  }

  onSubmit() {
    this.disabled = true;
    const v = this.roomEdit.value;
    const room: Room = {
      roomNumber: v.roomNumber,
      vlan: v.vlan,
      description: v.description
    };
    this.roomService.roomRoomNumberPut(v.roomNumber, room, 'response')
      .takeWhile(() => this.alive)
      .subscribe((response) => {
        this.router.navigate(['/room/view', v.roomNumber]);
        this.notif.success(response.status + ': Success');
      });
    this.disabled = false;
  }

  ngOnInit() {
    this.route.paramMap
      .switchMap((params: ParamMap) =>
        this.roomService.roomRoomNumberGet(+params.get('roomNumber')))
      .takeWhile(() => this.alive)
      .subscribe((room: Room) => {
        this.room = room;
        this.roomEdit.patchValue(room);
      });
  }

  ngOnDestroy() {
    this.alive = false;
  }

}
