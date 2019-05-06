import {Component, OnDestroy, OnInit} from '@angular/core';
import {Observable} from 'rxjs/Observable';
import {PortService} from '../api/api/port.service';
import {Port} from '../api/model/port';
import {ActivatedRoute, Router} from '@angular/router';
import {NotificationsService} from 'angular2-notifications';

@Component({
  selector: 'app-port-details',
  templateUrl: './port-details.component.html',
  styleUrls: ['./port-details.component.css']
})
export class PortDetailsComponent implements OnInit, OnDestroy {

  port$: Observable<Port>;
  portID: number;
  switchID: number;
  port_ouverture = 'ouvert';
  portouvert = true;
  port_authenth = 'authentifié';
  isportauthenth = false;
  private sub: any;

  constructor(
    public portService: PortService,
    private route: ActivatedRoute,
    private router: Router,
    private notif: NotificationsService,
  ) {
  }

  ouverture() {
    this.portouvert = !this.portouvert;
  }

  authenth() {
    this.isportauthenth = !this.isportauthenth;
  }

  IfRoomExists(roomNumber) {
    if (roomNumber == null) {
      this.notif.error('This port is not assigned to a room');
    } else {
      this.router.navigate(['/room/view', roomNumber]);
    }
  }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.switchID = +params['switchID'];
      this.portID = +params['portID'];
      this.port$ = this.portService.portPortIdGet(this.portID);
    });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

}
