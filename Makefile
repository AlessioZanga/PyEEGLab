.PHONY: tuh_eeg_abnormal tuh_eeg_artifact eegmmidb clean

tuh_eeg_abnormal:
	echo "Request your access password at: https://www.isip.piconepress.com/projects/tuh_eeg/html/request_access.php"
	rsync -auxvL nedc_tuh_eeg@www.isip.piconepress.com:~/data/tuh_eeg_abnormal/ data/tuh_eeg_abnormal

tuh_eeg_artifact:
	echo "Request your access password at: https://www.isip.piconepress.com/projects/tuh_eeg/html/request_access.php"
	rsync -auxvL nedc_tuh_eeg@www.isip.piconepress.com:~/data/tuh_eeg_artifact/ data/tuh_eeg_artifact

eegmmidb:
	wget -r -N -c -np https://physionet.org/files/eegmmidb/1.0.0/ -P data

clean:
	find -L data -iname "*.fif.gz" -type f -delete
