import matplotlib.pyplot as plt
import liesl
import os
# %%


if __name__ == '__main__':
    import argparse
    description = """Show an LSL stream in realtime
     
                  Example:
       
                  liesl.show type=EEG
          
                  you can add additional arguments to select the stream better 
      
                  liesl.show type=EEG hostname=localhost
            
                  or finetune the buffer duration or which channel to plot
       
                  liesl.show type=EEG --duration 2000 chan 0
                  """
                  
    parser = argparse.ArgumentParser(description=description)    


    parser.add_argument('kwargs', action='append', nargs='+',
                        type=lambda kv: kv.split("="),
                        help='Add kwargs for stream selection, e.g. type=EEG',
                        )                  

    parser.add_argument('--chan', type=int, default=None, help='Which channel to show')
    parser.add_argument('--duration', type=int, help='Buffer duration in ms',
                        default=1000)
      
    args = parser.parse_args()    
    kwargs = {}
    print('Looking for stream with the following parameters: ', end='')
    for k,v in dict(args.kwargs[0]).items():
        if v is not None:
            kwargs[k] = v
            print(f'{k} = {v}', end='')
    print('\n')
    stream = liesl.open_stream(**kwargs)
    print('Found!')
    buffer = liesl.RingBuffer(stream, duration_in_ms=args.duration)
    buffer.start()
    fig, ax = plt.subplots(1,1)
    while plt.fignum_exists(fig.number):
        plt.pause(0.05)
        ax.cla()    
        if args.chan is not None:
            ax.plot(buffer.get()[:, args.chan])
        else:
            ax.plot(buffer.get())
    else:        
        os._exit(0)

      
